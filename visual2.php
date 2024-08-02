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
$error = ''; // Variabel untuk menyimpan pesan kesalahan

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['nerButton'])) {
        $inputText = trim($_POST['inputText'] ?? '');
        
        // Validasi input tidak boleh kosong
        if (empty($inputText)) {
            $error = 'Teks tidak boleh kosong.';
        } else {
            $nerResult = processNER($inputText);
        }
    }
}


// Mengambil data label bencana dan jumlah tweet untuk setiap label
$sql = "SELECT label, COUNT(*) as total_tweets FROM clusters GROUP BY label";
$result = $conn->query($sql);

$labelData = [];
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $label = $row['label'];
        $totalTweets = $row['total_tweets'];

        // Menambahkan data label dan jumlah tweet ke dalam array
        $labelData[$label] = $totalTweets;
    }
}

// Mengambil data cluster name berdasarkan jumlah label terbanyak dari masing-masing cluster
$clusterNames = [];
$sqlClusterNames = "SELECT Cluster_ID, label, COUNT(label) as label_count FROM clusters GROUP BY Cluster_ID, label ORDER BY Cluster_ID, label_count DESC";
$resultClusterNames = $conn->query($sqlClusterNames);

if ($resultClusterNames->num_rows > 0) {
    $currentClusterID = null;
    $clusterIndex = 1;
    while ($row = $resultClusterNames->fetch_assoc()) {
        if ($currentClusterID != $row['Cluster_ID']) {
            $currentClusterID = $row['Cluster_ID'];
            $clusterNames[$currentClusterID] = [
                'label' => $row['label'],
                'index' => $clusterIndex
            ];
            $clusterIndex++;
        }
    }
}

// Mengambil data cluster dengan bencana terbanyak dari tabel clusters
$disasterClusters = [];
$sqlDisasterClusters = "SELECT Cluster_ID, label FROM clusters GROUP BY Cluster_ID, label ORDER BY Cluster_ID";
$resultDisasterClusters = $conn->query($sqlDisasterClusters);

if ($resultDisasterClusters->num_rows > 0) {
    while ($row = $resultDisasterClusters->fetch_assoc()) {
        $label = $row['label'];
        $clusterID = $row['Cluster_ID'];

        // Mengelompokkan berdasarkan jenis label (misal: 'banjir', 'gempa', 'tanah longsor', dll.)
        if (!isset($disasterClusters[$label])) {
            $disasterClusters[$label] = [];
        }
        $disasterClusters[$label][] = $clusterID;
    }
}


/// Mengambil data purity dari database
$sqlPurity = "SELECT Cluster_ID, Purity, jumlah_tweet FROM purity_results";
$resultPurity = $conn->query($sqlPurity);

$totalPurity = 0;
$totalWeightedPurity = 0;
$totalTweets = 0;
$totalClusters = 0;
$goodPurityClusters = [];
$badPurityClusters = [];

if ($resultPurity->num_rows > 0) {
    while ($row = $resultPurity->fetch_assoc()) {
        $clusterID = $row['Cluster_ID'];
        $purity = $row['Purity'];
        $jumlahTweet = $row['jumlah_tweet'];

        // Hitung total weighted purity
        $totalWeightedPurity += $purity * $jumlahTweet;
        $totalTweets += $jumlahTweet;
        $totalClusters++;

        // Klasifikasikan cluster ke dalam baik atau buruk
        if ($purity > 0.5) {
            $goodPurityClusters[] = $clusterID;
        } else {
            $badPurityClusters[] = $clusterID;
        }
    }
}



// Menghitung overall purity
$overallPurity = $totalTweets ? $totalWeightedPurity / $totalTweets * 100 : 0;



// Fungsi untuk memformat hasil NER
function formatNERResult($nerResult) {
    $html = '';
    $colors = [
        'person' => 'blue',
        'organization' => 'blue',
        'disaster' => 'blue',
        'location' => 'blue',
        'day' => 'blue',
        'date' => 'blue',
        'other' => 'blue'
    ];

    foreach ($nerResult as $token) {
        $word = htmlspecialchars($token['teks_kata']);
        $type = htmlspecialchars($token['type_ner']);
        $color = isset($colors[$type]) ? $colors[$type] : 'blue';
        $html .= "<span style=\"color: black;\">$word</span> (<a href=\"#\" style=\"color: $color;\">$type</a>), ";
    }

    return rtrim($html, ', ');
}

// Mengambil lokasi teratas dari analisis berdasarkan kategori klaster yang memiliki kategori "banjir", "gempa bumi", atau "tanah longsor"
$topLocations = [];
$categories = [
    'gempa bumi' => ['gempa bumi'],
    'tanah longsor' => ['tanah longsor'],
    'banjir tanah longsor' => ['banjir tanah longsor'],
    'banjir' => ['banjir', 'banjirrob', 'banjir bandang', 'laha lahar', 'banjir sungai']
];

foreach ($categories as $category => $labels) {
    $locations = [];
    $clusters = [];
    
    $labelList = "'" . implode("', '", $labels) . "'";
    $sqlTopLocations = "SELECT a.location, c.Cluster_ID FROM analisis a 
                        JOIN clusters c ON a.kategori_klaster = c.label 
                        WHERE c.label IN ($labelList)";
    $resultTopLocations = $conn->query($sqlTopLocations);

    if ($resultTopLocations->num_rows > 0) {
        while ($row = $resultTopLocations->fetch_assoc()) {
            $locations[] = $row['location'];
            $clusters[] = $row['Cluster_ID'];
        }
    }

    // Menghitung lokasi terbanyak untuk kategori ini
    $locationCounts = array_count_values($locations);
    arsort($locationCounts);
    $topLocation = !empty($locationCounts) ? key($locationCounts) : 'N/A';

    $topLocations[$category] = [
        'top_location' => $topLocation,
        'locations' => implode(', ', array_unique($locations)), // Menggabungkan lokasi dengan koma
        'clusters' => implode(', ', array_unique($clusters)) // Menggabungkan klaster dengan koma
    ];
}


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
            flex: 1 1 45%; /* Mengubah lebar konten menjadi 45% */
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
                        <input type="text" class="form-control" id="inputText" name="inputText" placeholder="Masukkan teks di sini..." value="<?php echo htmlspecialchars($inputText); ?>" required>
                        <div class="input-group-append">
                            <button class="btn btn-warning" type="submit" name="nerButton">NER</button>
                        </div>
                    </div>
                    <?php if (!empty($error)): ?>
                        <div class="text-danger mt-2"><?php echo htmlspecialchars($error); ?></div>
                    <?php endif; ?>
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

        <!-- Konten Kedua (Grafik Label Bencana) -->
        <div class="content-box">
            <canvas id="labelChart" width="400" height="300"></canvas>
        </div>
        <div class="content-box">
        <?php if (!empty($labelData)): ?>
            <div class="summary-card mt-3">
                <h5>Bencana Terbanyak</h5>
                <?php
                arsort($labelData);
                $topLabels = array_keys($labelData);
                ?>
                <ol>
                    <?php for ($i = 0; $i < min(3, count($topLabels)); $i++): ?>
                        <li><strong><?php echo $topLabels[$i]; ?></strong> dengan <?php echo $labelData[$topLabels[$i]]; ?> tweet</li>
                    <?php endfor; ?>
                </ol>
            </div>
        <?php endif; ?>
        <div class="summary-card">
            <h5>Hasil Pengujian Purity</h5>
            <p>Purity: <?= number_format($overallPurity, 2); ?>%</p>
        </div>

        </div>

        
        
        <!-- Konten Keempat (Kategori Klaster) -->
        <div class="content-box">
          <?php if (!empty($clusterNames)): ?> 
                <div class="summary-card mt-3">
                    <h5>Kategori Klaster:</h5>
                    <div style="column-count: 2;">
                        <?php foreach ($clusterNames as $clusterId => $clusterInfo): ?>
                            <p><strong><?php echo $clusterInfo['index']; ?>.</strong> <?php echo $clusterInfo['label']; ?></p>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>
        </div> 

     <!-- Konten untuk lokasi teratas dari analisis -->
    <div class="content-box">
        <?php if (!empty($topLocations)): ?>
            <div class="summary-card mt-3">
                <h5>Lokasi Bencana dari Klaster:</h5>
                <table class="table table-striped table-bordered">
                    <thead>
                        <tr>
                            <th>Kategori</th>
                            <th>Top lokasi</th>
                            <th>Hasi ekstak lokasi</th>
                            <th>Klaster</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($topLocations as $category => $data): ?>
                            <tr>
                                <td><?php echo ucfirst($category); ?></td>
                                <td><?php echo $data['top_location']; ?></td>
                                <td><?php echo $data['locations']; ?></td>
                                <td><?php echo $data['clusters']; ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>

    <script>
        // Menggambar grafik label bencana
        var ctxLabel = document.getElementById('labelChart').getContext('2d');
        var labelData = <?php echo json_encode(array_values($labelData)); ?>;
        var labelNames = <?php echo json_encode(array_keys($labelData)); ?>;

        var labelChart = new Chart(ctxLabel, {
            type: 'bar',
            data: {
                labels: labelNames,
                datasets: [{
                    label: 'Jumlah Tweet per Label',
                    data: labelData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
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
                        text: 'Jumlah Tweet per Label Bencana'
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
