<?php


// Desactivar mensajes de error para producción
error_reporting(0);
ini_set('display_errors', 0);

// Headers
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Configuración de base de datos
$servidor = "localhost";
$usuario = "root";
$contrasena = "";
$baseDatos = "measure_datalog";
$puerto = 3307;

try {
    // Conectar a la base de datos
    $conn = new mysqli($servidor, $usuario, $contrasena, $baseDatos, $puerto);
    
    // Verificar conexión
    if ($conn->connect_error) {
        echo json_encode(['error' => 'Error de conexión']);
        exit;
    }
    
    // Configurar charset
    $conn->set_charset("utf8");
    
    // Consulta SQL
    $sql = "SELECT 
        id,
        temperatura,
        humedad,
        pm1_0,
        pm2_5,
        pm10,
        fecha
    FROM datos 
    ORDER BY fecha DESC 
    LIMIT 1000";
    
    $result = $conn->query($sql);
    
    $datos = [];
    
    if ($result && $result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $datos[] = [
                'id' => intval($row['id']),
                'temperatura' => floatval($row['temperatura']),
                'humedad' => floatval($row['humedad']),
                'pm1_0' => intval($row['pm1_0']),
                'pm2_5' => intval($row['pm2_5']),
                'pm25' => intval($row['pm2_5']),
                'pm10' => intval($row['pm10']),
                'radiacion' => 0,
                'fecha_hora' => $row['fecha']
            ];
        }
    }
    
    $conn->close();
    
    // Limpiar cualquier output buffer
    ob_clean();
    
    // Devolver JSON limpio
    echo json_encode($datos, JSON_NUMERIC_CHECK);
    
} catch (Exception $e) {
    ob_clean();
    echo json_encode(['error' => 'Error interno']);
}


?>