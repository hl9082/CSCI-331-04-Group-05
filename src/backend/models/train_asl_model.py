'''
train_asl_model.py
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
import random
from torchvision.datasets import ImageFolder


def balanced_subset(dataset, samples_per_class):
    """
    Creates a balanced subset of a dataset by sampling a fixed number of
    samples from each class.

    This function is useful for addressing class imbalance by ensuring
    each class is represented (up to) a specified number of times in
    the new subset.

    Args:
        dataset (torch.utils.data.Dataset): The original dataset. This
            dataset object must have a `.samples` attribute (a list of
            (sample, label) tuples) and a `.classes` attribute. This
            is standard for datasets like `torchvision.datasets.ImageFolder`.
        samples_per_class (int): The target number of samples to
            randomly select from each class. If a class has fewer
            total samples than this number, all samples from that
            class will be included.

    Returns:
        torch.utils.data.Subset: A new Subset object containing the
            balanced selection of indices from the original dataset.
    """
    # Create a list of lists to store indices for each class
    class_indices = [[] for _ in dataset.classes]
    
    # Populate the lists with indices for each sample's label
    for idx, (_, label) in enumerate(dataset.samples):
        class_indices[label].append(idx)
    selected_indices = []
    
    # Randomly sample from each class's index list
    for indices in class_indices:
        # Add the randomly sampled indices to our final list
        selected_indices.extend(random.sample(indices, min(samples_per_class, len(indices))))
    # Create and return a new Subset using the original dataset and the
    # new balanced list of indices    
    return torch.utils.data.Subset(dataset, selected_indices)

def main():

    class_labels = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "del", "space", "nothing"
    ]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data", "asl_alphabet_train", "asl_alphabet_train")
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
    balanced = balanced_subset(train_dataset, samples_per_class=32)

    # Use a small subset for quick testing
    subset_size = 32
    subset, _ = random_split(train_dataset, [subset_size, len(train_dataset) - subset_size]) # take small subset for quick testing
    
    train_loader = DataLoader(balanced, batch_size=32, shuffle=True, num_workers=0) # create data loader

    print(f"Loaded {len(subset)} images from {len(train_dataset.classes)} classes.")

    # Model setup
    print("Setting up model...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT) # load pre-trained MobileNetV2
    model.classifier[1] = nn.Linear(model.last_channel, len(class_labels))
    print("Model loaded")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()

    # Adaptive Moment Estimation (Adam) optimizer
    optimizer = optim.Adam(model.parameters()) # create optimizer

    # Training loop
    # trains a neural network using a dataset of labeled ASL images
    EPOCHS = 3  

    for epoch in range(EPOCHS):
        model.train() # Set model to training mode
        running_loss = 0.0 # track total loss
        print(f"Starting epoch {epoch+1}/{EPOCHS}...")
        # iterate through batches of training data (images, labels)
        for images, labels in train_loader:
            print(f"Processing batch of size {images.size(0)}")

            images, labels = images.to(device), labels.to(device) # move images, labels to (CPU or GPU)

            optimizer.zero_grad() # Clear the gradients from the previous batch
            outputs = model(images) # compute predicted outputs
            loss = criterion(outputs, labels) # compute loss
            loss.backward() # backpropagate: compute the gradients
            optimizer.step() # update model parameters
            running_loss += loss.item() * images.size(0) # loss += loss * batch_size

        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {running_loss/len(train_loader):.4f}")

    torch.save(model.state_dict(), SAVE_PATH) # save the trained model
    print(f"Model saved to {SAVE_PATH}")

if __name__ == "__main__":
    main()

