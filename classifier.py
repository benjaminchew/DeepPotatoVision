import torch
import torchvision.models as models
import torch.optim as optim
from torchvision import datasets, transforms
from load_imglist import ImageList, rgb_loader
import torch.nn.functional as F
from torch.autograd import Variable
from PIL import Image

savefile_model = 'classifier_model/vgg16_pretrained.pt'
vgg16 = models.vgg16(pretrained=True)
#torch.save(vgg16.state_dict(), savefile_model)


def get_model(savefile_model):
    model = models.vgg16()
    model.load_state_dict(torch.load(savefile_model))
    ct = 0
    for child in model.children():
        ct += 1
        if ct < 3:
            for param in child.parameters():
                param.requires_grad = False
    return model

#0.485, 0.456, 0.406],
#0.229, 0.224, 0.225]),
def load_data_set(batch_size = 20, set = 'train'):
    root_path = '/Users/benjaminchew/Documents/GitHub/DeepPotatoVision/'
    data_list = root_path+set+'.txt'
    data_loader = torch.utils.data.DataLoader(
        ImageList(root=root_path, fileList=data_list,
        transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]),
        ]),loader=rgb_loader),
        batch_size=batch_size, shuffle=True, #True,
        #num_workers=args.workers,
        pin_memory=True)
    return data_loader


def train(
          model,
          device,
          optimizer,
          epoch,
          ):
    print_interval = 200
    eval_interval = 200
    train_loader = load_data_set(set = 'train')
    test_loader = load_data_set(set = 'test')
    logs = []
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % print_interval == 0:
            print(
                  "[Train] Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                  epoch, batch_idx * len(data), len(train_loader.dataset),
                  100.0 * batch_idx / len(train_loader), loss.item(),))
        if batch_idx % eval_interval == 0:
            acc_train = evaluate(model, device, train_loader, training = True)
            acc_test = evaluate(model, device, test_loader)
            logs.append((epoch, batch_idx, acc_train, acc_test))
    return logs


def evaluate(model, device, data_loader, training=False):
    fold = "Train" if training else "Test"
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.cross_entropy(
               output, target, reduction="sum"
               ).item()
            pred = output.argmax(
               dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    test_loss /= len(data_loader.dataset)
    accuracy = correct / len(data_loader.dataset)
    print(
          "[Eval] {} set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f})".format(
           fold, test_loss, correct, len(data_loader.dataset), accuracy))
    return accuracy


def train_classifier(epochs=10, cmdline_args=None):
    dir = 'classifier_model/'
    batch_size_eval= 512
    learning_rate= 1e-2
    momentum= 0.8
    cutoff_ratio= 0.15
    cut_ratio = .2
    savefile_model = dir+'vgg16_pretrained.pt'
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    #data_loader = load_data_set(set = 'train')
    model = get_model(savefile_model).to(device)
    optimizer = optim.SGD(
       model.parameters(), lr=learning_rate, momentum=momentum)
    logs_train = []
    for epoch in range(1, epochs + 1):
        #print("+=+=+=+=+=+=")
        logs_train += train(
                            model, device, optimizer, epoch
                            )
    print("\n\n\n")
    #torch.save(seed_used, savefile_seed)
    file_trained_model = dir+'trained_classifier.pt'
    torch.save(model.state_dict(), file_trained_model)
    return logs_train

def img_process(image_file):
    
    image_file = Image.open(image_file)

    min_img_size = 224  # Size for PyTorch's pretrained models.
    transform_pipeline = transforms.Compose([transforms.Resize(min_img_size),
                                         transforms.ToTensor(),
                                         transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                              std=[0.229, 0.224, 0.225])])
    img = transform_pipeline(image_file)
    img = img.unsqueeze(0)
    img = Variable(img)
    return img