<?php
// Configuración de base de datos
$servidor = "localhost";
$usuario = "root";
$contrasena = "";
$baseDatos = "measure_datalog";
$puerto = 3307;

// Conectar a la base de datos
$conn = new mysqli($servidor, $usuario, $contrasena, $baseDatos, $puerto);

// Verificar conexión
if ($conn->connect_error) {
    die("❌ Error de conexión: " . $conn->connect_error);
}

// Recibir datos del ESP32
$temperatura = $_POST['temperatura'];
$humedad = $_POST['humedad'];
$pm1_0 = $_POST['pm1_0'];
$pm2_5 = $_POST['pm2_5'];
$pm10 = $_POST['pm10'];

// Insertar en la base de datos
$sql = "INSERT INTO datos (temperatura, humedad, pm1_0, pm2_5, pm10) 
        VALUES ('$temperatura', '$humedad', '$pm1_0', '$pm2_5', '$pm10')";

if ($conn->query($sql) === TRUE) {
    echo "✅ Datos guardados correctamente";
} else {
    echo "❌ Error: " . $conn->error;
}

$conn->close();
?>