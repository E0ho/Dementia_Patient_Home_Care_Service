import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.transforms import transforms

# 모델 클래스 정의
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        # 모델 구현

# 모델과 데이터 로더 초기화
model = MyModel()
model.load_state_dict(torch.load('Models/TSSTG/tsstg-model.pth'))
model.eval()

test_transforms = transforms.Compose([
    # test data 변환
])

test_dataset = DataLoader.MyDataset('Data/FallDataset/Home_01/videos', transform=test_transforms)
test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# 평가 함수 정의
def evaluate(model, test_dataloader):
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for inputs, labels in test_dataloader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            total_samples += labels.size(0)
            total_correct += (predicted == labels).sum().item()

    accuracy = total_correct / total_samples
    return accuracy

# 평가 실행
accuracy = evaluate(model, test_dataloader)
print('Test accuracy: {:.2f}%'.format(accuracy*100))
