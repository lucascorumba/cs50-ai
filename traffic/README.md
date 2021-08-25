# Neural Networks - Traffic
 AI that identifies which traffic sign appears in a photograph.
 
## Database
* Download the [data set](https://cdn.cs50.net/ai/2020/x/projects/5/gtsrb.zip) (about 180Mb) and unzip it. Move the resulting ``gtsrb`` directory inside the ``traffic`` directory.
    * This is the [German Traffic Sign Recognition Benchmark (GTSRB)](http://benchmark.ini.rub.de/?section=gtsrb&subsection=news) dataset, which contains thousands of images of 43 different kinds of road signs.
 
## Experimentation
A convolutional neural network was built using the source code of lecture 5 as foundation. 
After that, changes were made in order to verify what effect each one would have in the model's loss and accuracy. The modifications were cumulative, and the submitted code was the result of the test number **10**.

### Base model
The **'Lecture based model'** had the following structure:
* 1 Convolutional layer, learning 32 filters using a 3x3 kernel
* 1 max-pooling layer, using a 2x2 pool size
* 1 hidden layer with 128 nodes with 0.5 dropout rate
* output layer with 1 unit for each traffic sign

## Results

| Test | Modification | Loss | Accuracy |
| :----| :----------- | :--- |:-------- |
| 1  | Lecture based model| *3.4942* | *0.0556* |
| 2  | Convolutional layer learning 42 filters and activation function 'ReLu' | *1.4159* | *0.5556* |
| 3  | Add second hidden layer with 64 units and activation function 'ReLu', dropout rate 0.5. Dropout rate from existing hidden layer removed  | *0.5031* | *0.8662* |
| 4  | Convolutional layer learning 84 filters | *0.3614* | *0.9182* |
| 5  | Add max-pooling layer using 2x2 pool size | *0.6467* | *0.7857* |
| 6  | Undo changes made on test **5**. Add one hidden layer with 16 units and activation function 'ReLu' | *3.4978* | *0.0554* |
| 7  | Undo changes made on test **6**. Add second convolutional layer, learning 21 filters using a 2x2 kernel, and activation function 'ReLu' | *0.2065* | *0.9488* |
| 8  | Add a third convolution layer, identical to the second | *0.1288* | *0.9725* |
| 9  | Undo changes made on test **8**. Add dropout (0.3) to hidden layer with 128 units | *0.2060* | *0.9507* |
| 10 | Decreased dropout rate of second hidden layer to 0.3 | *0.1946* | *0.9480* |

## Discussion
As expected, the lecture based model had a poor accuracy. Simply increasing the number of filters was already enough to improve the performance tenfolds. Adding a second hidden layer improved the performance even more, reaching a more decent accuracy. Adding an extra max-pooling layer noticeably decreased accuracy without improving processing time. Same for placing an extra hidden layer, wich reduced performance to base model levels. In general, the tests with best result were the ones where more convolutional layers and two hidden layers were present. Opposed to the addition of extra convolution layers, including more hidden layers to this setup showed a decline in performance. No other setting was able to surpass the accuracy reached when three convolutional layers were present.
