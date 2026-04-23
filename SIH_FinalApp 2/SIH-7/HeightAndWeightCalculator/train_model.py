import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv('training_data.csv')
X = df[['avg_rom', 'avg_velocity', 'weight_kg']]  # Features (weight as target)
y = df['weight_kg']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)
print(f"Error: {error:.2f} kg")

joblib.dump(model, 'weight_model.pkl')
joblib.dump(scaler, 'scaler.pkl')