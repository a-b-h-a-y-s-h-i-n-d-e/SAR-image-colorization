import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms

from dataset import SAROpticalDataset
from model import UNet

transform = transforms.Compose([
    transforms.Resize((256, 256)),  # Adjust to your model's input size
    transforms.ToTensor()
])

data = SAROpticalDataset(root_dir="/dataset/", transform=transform)

train_dataset, val_dataset = random_split(data, [0.8, 0.2])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
valid_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

model = UNet(n_class=3).to(device)
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 10
for epoch in range(1, num_epochs+1):
    model.train()

    train_loss = 0.0
    for sar_img, opt_img in train_loader:
        sar_img, opt_img = sar_img.to(device), opt_img.to(device)
        optimizer.zero_grad()
        color_img = model(sar_img)
        loss = criterion(color_img, opt_img)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()*sar_img.size(0)

    train_loss = train_loss/len(train_loader.dataset)

    model.eval()

    valid_loss = 0.0
    with torch.no_grad():
        for sar_img, opt_img in valid_loader:
            sar_img, opt_img = sar_img.to(device), opt_img.to(device)
            color_img = model(sar_img)
            loss = criterion(color_img, opt_img)

            valid_loss += loss.item()*sar_img.size(0)

    valid_loss = valid_loss/len(valid_loader.dataset)

    print(f'Epoch {epoch}/{num_epochs} | Train_loss: {train_loss:.4f} | Validation loss: {valid_loss:.4f}')

# Save the model after training
torch.save({
    'epoch': num_epochs,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'train_loss': train_loss,
    'valid_loss': valid_loss,
}, 'final_model.pth')

print(f'Model saved after {num_epochs} epochs')
