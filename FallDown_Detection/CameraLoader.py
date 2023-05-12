import os
import cv2
import time
import torch
import numpy as np

from queue import Queue
from threading import Thread, Lock


class CamLoader:

    def __init__(self, camera, preprocess=None, ori_return=False):

        # 실시간 webcam 사용
        self.stream = cv2.VideoCapture(0)
        
        assert self.stream.isOpened(), 'Cannot read camera source!'
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        self.frame_size = (int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        self.stopped = False
        self.ret = False
        self.frame = None
        self.ori_frame = None
        self.read_lock = Lock()
        self.ori = ori_return

        self.preprocess_fn = preprocess

    def start(self):
        self.t = Thread(target=self.update, args=())  # , daemon=True)
        self.t.start()
        c = 0
        while not self.ret:
            time.sleep(0.1)
            c += 1
            if c > 20:
                self.stop()
                raise TimeoutError('Can not get a frame from camera!!!')
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.stream.read()
            self.read_lock.acquire()
            self.ori_frame = frame.copy()
            if ret and self.preprocess_fn is not None:
                frame = self.preprocess_fn(frame)

            self.ret, self.frame = ret, frame
            self.read_lock.release()

    def grabbed(self):
        """Return `True` if can read a frame."""
        return self.ret

    def getitem(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        ori_frame = self.ori_frame.copy()
        self.read_lock.release()
        if self.ori:
            return frame, ori_frame
        else:
            return frame

    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        if self.t.is_alive():
            self.t.join()
        self.stream.release()

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream.isOpened():
            self.stream.release()


class CamLoader_Q:

    # Thread, Queue를 활용하여 video Frame을 순차 처리
    """
    Args:
        camera: (int, str) Source of camera or video.,
        batch_size: (int) Number of batch frame to store in queue. Default: 1,
        queue_size: (int) Maximum queue size. Default: 256,
        preprocess: (Callable function) to process the frame before return.
    """
    def __init__(self, camera, batch_size=1, queue_size=256, preprocess=None):
        self.stream = cv2.VideoCapture(camera)
        assert self.stream.isOpened(), 'Cannot read camera source!'
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        self.frame_size = (int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # 각 프레임 Queue 저장

        self.stopped = False
        self.batch_size = batch_size
        self.Q = Queue(maxsize=queue_size)

        self.preprocess_fn = preprocess

    def start(self):
        t = Thread(target=self.update, args=(), daemon=True).start()
        c = 0
        while not self.grabbed():
            time.sleep(0.1)
            c += 1
            if c > 20:
                self.stop()
                raise TimeoutError('Can not get a frame from camera!!!')
        return self

    def update(self):
        while not self.stopped:
            if not self.Q.full():
                frames = []
                for k in range(self.batch_size):
                    ret, frame = self.stream.read()
                    if not ret:
                        self.stop()
                        return

                    if self.preprocess_fn is not None:
                        frame = self.preprocess_fn(frame)

                    frames.append(frame)
                    frames = np.stack(frames)
                    self.Q.put(frames)
            else:
                with self.Q.mutex:
                    self.Q.queue.clear()
            # time.sleep(0.05)

    def grabbed(self):
        """Return `True` if can read a frame."""
        return self.Q.qsize() > 0

    def getitem(self):
        return self.Q.get().squeeze()

    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        self.stream.release()

    def __len__(self):
        return self.Q.qsize()

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream.isOpened():
            self.stream.release()


if __name__ == '__main__':
    fps_time = 0

    # Threading 사용
    cam = CamLoader(0).start()
    while cam.grabbed():
        frames = cam.getitem()

        frames = cv2.putText(frames, 'FPS: %f' % (1.0 / (time.time() - fps_time)),
                             (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        fps_time = time.time()
        cv2.imshow('frame', frames)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stop()
    cv2.destroyAllWindows()
