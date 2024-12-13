import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import numpy as np
from collections import defaultdict

dataset_name = "food101"
(raw_train, raw_test), metadata = tfds.load(
    dataset_name,
    split=["train", "validation"],
    as_supervised=True,
    with_info=True
)

def preprocess_image(image, label):
    image = tf.image.resize(image, (224, 224))
    image = tf.keras.applications.efficientnet.preprocess_input(image)
    return image, label


def augment_image(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta=0.2)
    image = tf.image.random_contrast(image, lower=0.8, upper=1.2)
    image = tf.image.random_crop(tf.image.resize_with_crop_or_pad(image, 250, 250), size=[224, 224, 3])
    return image, label

# Batch size
batch_size = 32

AUTOTUNE = tf.data.AUTOTUNE

train = (raw_train
         .map(preprocess_image, num_parallel_calls=AUTOTUNE)
         .map(augment_image, num_parallel_calls=AUTOTUNE)
         .shuffle(1000)
         .batch(batch_size)
         .prefetch(AUTOTUNE))

test = (raw_test
        .map(preprocess_image, num_parallel_calls=AUTOTUNE)
        .batch(batch_size)
        .prefetch(AUTOTUNE))

base_model = EfficientNetB3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the base model

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(101, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
initial_epochs = 10
history = model.fit(train, validation_data=test, epochs=initial_epochs)

for layer in base_model.layers[-50:]:
    layer.trainable = True

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6)
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Continue training
fine_tune_epochs = 15
total_epochs = initial_epochs + fine_tune_epochs

history_fine = model.fit(train, validation_data=test, epochs=total_epochs, initial_epoch=history.epoch[-1], callbacks=[reduce_lr, early_stopping])

test_loss, test_accuracy = model.evaluate(test)
print(f"Test Accuracy: {test_accuracy:.2f}")

label_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})

for images, labels in test:
    predictions = model.predict(images)
    predicted_labels = np.argmax(predictions, axis=1)

    for true_label, predicted_label in zip(labels.numpy(), predicted_labels):
        label_accuracy[true_label]["total"] += 1
        if true_label == predicted_label:
            label_accuracy[true_label]["correct"] += 1

label_accuracy = {
    label: acc["correct"] / acc["total"] if acc["total"] > 0 else 0
    for label, acc in label_accuracy.items()
}

sorted_labels = sorted(label_accuracy.items(), key=lambda x: x[1], reverse=True)

top_20_labels = sorted_labels[:50]

class_names = metadata.features['label'].int2str  # Konversi indeks ke nama kelas
for label, accuracy in top_20_labels:
    print(f"Label: {class_names(label)}, Accuracy: {accuracy:.2%}")