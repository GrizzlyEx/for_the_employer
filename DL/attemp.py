import numpy as np
from sklearn.linear_model import LinearRegression

x_train = np.array([[1],[2],[3]])
y_train = np.array([-1.2,-2.3,-3.4])
model = LinearRegression()
model.fit(x_train, y_train)
x_test = np.array([[1100],[1110],[1210]])
y_pred = model.predict(x_test)
print(y_pred)