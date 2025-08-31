from tensorflow.keras.preprocessing.image import ImageDataGenerator

dataset_path = "./dataset"  # Point to your dataset folder

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(128,128),
    batch_size=8,
    class_mode='categorical',
    subset='training'
)

val_gen = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(128,128),
    batch_size=8,
    class_mode='categorical',
    subset='validation'
)
