<?php
ob_start();

// Koneksi ke database
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "databanjir";  // Ganti dengan nama database Anda

$conn = new mysqli($servername, $username, $password, $dbname);

// Periksa koneksi
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fungsi untuk memanggil skrip Python untuk NER
function processNER($input) {
    $escapedInput = escapeshellarg($input);
    $command = "python ner_new.py $escapedInput";
    $output = shell_exec($command);
    return json_decode($output, true);
}

$nerResult = [];
$inputText = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['nerButton'])) {
        $inputText = $_POST['inputText'] ?? '';
        $nerResult = processNER($inputText);
    }
}

// Mengambil data lokasi dan menghitung jumlah tweet untuk setiap lokasi
$sql = "SELECT location, COUNT(*) as total_tweets FROM analisis GROUP BY location";
$result = $conn->query($sql);

$locationData = [];
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $location = $row['location'];
        $totalTweets = $row['total_tweets'];

        // Menambahkan data lokasi dan jumlah tweet ke dalam array
        $locationData[$location] = $totalTweets;
    }
}

// Mengambil kluster yang terkait dengan Sumatra dari tabel analisis
$sumatraClusters = [];
$sqlClusters = "SELECT DISTINCT Cluster_ID FROM analisis WHERE location LIKE '%Sumatra%'";
$resultClusters = $conn->query($sqlClusters);
if ($resultClusters->num_rows > 0) {
    while ($row = $resultClusters->fetch_assoc()) {
        $sumatraClusters[] = $row['Cluster_ID'];
    }
}

// Fungsi untuk memformat hasil NER
function formatNERResult($nerResult) {
    $html = '';
    $colors = [
        'person' => '#007bff',        // Blue
        'organization' => '#007bff',  // Blue
        'disaster' => '#007bff',      // Blue
        'location' => '#007bff',      // Blue
        'day' => '#007bff',           // Blue
        'date' => '#007bff',          // Blue
        'other' => '#000000'          // Black
    ];

    foreach ($nerResult as $token) {
        $word = htmlspecialchars($token['teks_kata']);
        $type = htmlspecialchars($token['type_ner']);
        $color = isset($colors[$type]) ? $colors[$type] : '#007bff'; // Default to blue if type is not found
        $html .= "<span style=\"color: black;\">$word</span> (<a href=\"#\" style=\"color: $color;\">$type</a>), ";
    }

    return rtrim($html, ', ');
}

// Mengambil dua lokasi terdampak tertinggi
$sqlTopLocations = "SELECT location, COUNT(*) as total_tweets FROM analisis GROUP BY location ORDER BY COUNT(*) DESC LIMIT 2";
$resultTopLocations = $conn->query($sqlTopLocations);
$topLocations = [];
if ($resultTopLocations->num_rows > 0) {
    while ($row = $resultTopLocations->fetch_assoc()) {
        $location = $row['location'];
        $topLocations[] = $location;
    }
}

// Mengambil data purity dari database
$sqlPurity = "SELECT Cluster_ID, Purity FROM purity_results";
$resultPurity = $conn->query($sqlPurity);

$purityData = [];
$goodPurityClusters = [];
$badPurityClusters = [];
$totalPurity = 0;
$totalClusters = 0;
if ($resultPurity->num_rows > 0) {
    while ($row = $resultPurity->fetch_assoc()) {
        $purityData[$row['Cluster_ID']] = $row['Purity'];
        if ($row['Purity'] > 0.5) {
            $goodPurityClusters[] = $row['Cluster_ID'];
        } else {
            $badPurityClusters[] = $row['Cluster_ID'];
        }
        $totalPurity += $row['Purity'];
        $totalClusters++;
    }
}

// Mengambil cluster_name dari tabel analisis berdasarkan Cluster_ID
$clusterNames = [];
$sqlClusterNames = "SELECT DISTINCT Cluster_ID, cluster_name FROM analisis";
$resultClusterNames = $conn->query($sqlClusterNames);
if ($resultClusterNames->num_rows > 0) {
    while ($row = $resultClusterNames->fetch_assoc()) {
        $clusterNames[$row['Cluster_ID']] = $row['cluster_name'];
    }
}

// Menghitung rata-rata purity
$averagePurity = $totalClusters ? $totalPurity / $totalClusters : 0;

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualisasi Hasil</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #f5f5f5;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        .content-box {
            flex: 1 1 30%; /* Mengubah lebar konten menjadi 30% */
            padding: 10px;
            margin: 10px;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .content-box.large {
            flex: 1 1 100%;
        }
        .ner-result {
            border: 1px solid #007bff;
            padding: 10px;
            margin-top: 10px;
            white-space: pre-wrap;
            background-color: #f9f9f9;
        }
        .summary-card {
            padding: 10px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .summary-card h5 {
            margin: 0;
            padding: 0;
            font-size: 1.1rem;
        }
        .summary-card p {
            margin: 5px 0 0;
        }
        .table-purity {
            margin-top: 20px;
            width: auto;
            font-size: 12px;
        }
        .table-purity th, .table-purity td {
            padding: 5px;
        }
        canvas {
            display: block;
            margin: auto;
        }
    </style>
</head>
<body>
    <div class="container mt-3">
        <!-- Konten Pertama (Hasil NER) -->
        <div class="content-box large">
            <form method="post" action="">
                <div class="form-group">
                    <label for="inputText">Masukkan Teks untuk Ekstraksi NER:</label>
                    <div class="input-group">
                        <input type="text" class="form-control" id="inputText" name="inputText" placeholder="Masukkan teks di sini..." value="<?php echo htmlspecialchars($inputText); ?>">
                        <div class="input-group-append">
                            <button class="btn btn-warning" type="submit" name="nerButton">NER</button>
                        </div>
                    </div>
                </div>
            </form>
            <?php if (!empty($nerResult)): ?>
                <div class="summary-card">
                    <h5>Hasil NER</h5>
                    <div class="ner-result">
                        <?php echo formatNERResult($nerResult); ?>
                    </div>
                </div>
            <?php endif; ?>
        </div>

        <!-- Konten Kedua (Grafik Lokasi) -->
        <div class="content-box">
            <canvas id="locationChart" width="400" height="300"></canvas>
            <?php if (!empty($locationData)): ?>
                <div class="summary-card mt-3">
                    <h5>Lokasi Terdampak Tertinggi:</h5>
                    <?php if (isset($topLocations[0])): ?>
                        <p>1. <strong><?php echo $topLocations[0]; ?></strong></p>
                    <?php endif; ?>
                    <?php if (isset($topLocations[1])): ?>
                        <p>2. <strong><?php echo $topLocations[1]; ?></strong></p>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
        </div>
         <!-- Konten Keempat (Kluster Sumatra dan Purity) -->
         <div class="content-box">
            <?php if (!empty($sumatraClusters)): ?>
                <div class="summary-card">
                    <h5>Kluster yang Terkait dengan Sumatra:</h5>
                    <p><?php echo implode(', ', $sumatraClusters); ?></p>
                </div>
            <?php endif; ?>

            <?php if (!empty($goodPurityClusters) || !empty($badPurityClusters)): ?>
                <div class="summary-card">
                    <h5>Purity Baik</h5>
                    <p>Jumlah kluster dengan purity baik (>50%): <?php echo count($goodPurityClusters); ?></p>
                    <p>Kluster dengan purity baik: <?php echo implode(', ', $goodPurityClusters); ?></p>
                </div>
                <div class="summary-card">
                    <h5>Purity Buruk</h5>
                    <p>Jumlah kluster dengan purity buruk (<=50%): <?php echo count($badPurityClusters); ?></p>
                    <p>Kluster dengan purity buruk: <?php echo implode(', ', $badPurityClusters); ?></p>
                </div>
            <?php endif; ?>

            <div class="summary-card">
                <h5>Rata-rata Purity</h5>
                <p><?php echo number_format($averagePurity, 2); ?></p>
            </div>
        </div>
    </div>

        <!-- Konten Ketiga (Cluster Names) -->
        <div class="content-box">
            <?php if (!empty($clusterNames)): ?>
                <div class="summary-card mt-3">
                    <h5>Cluster Names:</h5>
                    <?php foreach ($clusterNames as $clusterId => $clusterName): ?>
                        <p><strong><?php echo $clusterId; ?>:</strong> <?php echo $clusterName; ?></p>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
        
    <script>
        var locationData = <?php echo json_encode($locationData); ?>;
        var locationLabels = Object.keys(locationData);
        var tweetCounts = Object.values(locationData);

        var ctx = document.getElementById('locationChart').getContext('2d');
        var locationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: locationLabels,
                datasets: [{
                    label: 'Jumlah Tweet per Lokasi',
                    data: tweetCounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return tooltipItem.raw;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Jumlah Tweet per Lokasi Terdampak'
                    }
                }
            }
        });
    </script>
</body>
</html>

<?php
$title = "Visualisasi Hasil";
$page_title = "Visualisasi";
$content = ob_get_clean();
include 'layout.php'; // Gantilah dengan file layout yang sesuai dengan struktur aplikasi Anda
?>
