'''
 @author Will Stott (wjs8666)
  @co-author Huy Le, Zoe Shearer, Josh Elliot
  @purpose
    This script trains a MobileNetV2 model on the ASL alphabet dataset.
     It preprocesses the images, sets up the model, and runs a training loop.
  @importance
    This file is used to create and train the ASL recognition model that powers
    the ASL translation service in the application.
    
'''

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split

import os

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = "data/asl_alphabet_train/kaggleASLDataset/asl_alphabet_test"
    SAVE_PATH = os.path.join(BASE_DIR, "asl_model.pth")

    # Data transformations
    transform = transforms.Compose([
        transforms.Resize((32, 32)),  
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    # Load dataset
    print("Loading dataset...")
    train_dataset = datasets.ImageFolder(root=DATA_DIR, transform=transform)

    # Use a small subset for quick testing
    subset_size = 5000
    subset, _ = random_split(train_dataset, [subset_size, len(train_dataset) - subset_size])
    train_loader = DataLoader(subset, batch_size=32, shuffle=True, num_workers=0)

    print(f"Loaded {len(subset)} images from {len(train_dataset.classes)} classes.")

    # Model setup
    print("Setting up model...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.last_channel, len(train_dataset.classes))
    print("Model loaded")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    EPOCHS = 3  
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        print(f"Starting epoch {epoch+1}/{EPOCHS}...")
        for images, labels in train_loader:
            print(f"Processing batch of size {images.size(0)}")
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {running_loss/len(train_loader):.4f}")

    torch.save(model.state_dict(), SAVE_PATH)
    print(f"Model saved to {SAVE_PATH}")

if __name__ == "__main__":
    main()

