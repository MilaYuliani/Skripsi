<?php
ob_start();

// Contoh data dokumen dan tweet
$data = [
    ['dokumen' => 'D1', 'tweet' => 'peduli bencana sumatra barat gadai salur bantu korban banjir bandang'],
    ['dokumen' => 'D2', 'tweet' => 'banjir bandang demak'],
    ['dokumen' => 'D3', 'tweet' => 'gempa bumi kuat magnitudo guncang kabupaten garut jawa barat sabtu malam'],
    ['dokumen' => 'D4', 'tweet' => 'banjir bandang tanah longsor terjang sumbawa'],
    ['dokumen' => 'D5', 'tweet' => 'gempa bumi kuat magnitudo jadi kabupaten pangandaran jawa barat ada dalam kilometer']
];

// Contoh data matriks kesamaan dokumen
$similarityMatrix = [
    [0, 0.18, 0.05, 0.14, 0.05],
    [0.18, 0,  0,    0.29,    0],
    [0.05, 0,  0,  0, 0.44],
    [0.14, 0.29, 0.10, 0, 0],
    [0.05, 0, 0.44, 0, 0]
];

// Fungsi untuk menyalin matriks
function copyMatrix($matrix) {
    return array_map(function($row) {
        return array_slice($row, 0);
    }, $matrix);
}

// Fungsi untuk menemukan nilai similarity minimum selain 0
function findMinSimilarity($matrix) {
    $min = INF;
    foreach ($matrix as $row) {
        foreach ($row as $value) {
            if ($value != 0 && $value < $min) {
                $min = $value;
            }
        }
    }
    return $min;
}

// Fungsi untuk menemukan pasangan dokumen dengan similarity maksimum
function findMaxSimilarityPair($matrix) {
    $max = 0;
    $pair = [];
    $size = count($matrix);
    for ($i = 0; $i < $size; $i++) {
        for ($j = 0; $j < $size; $j++) {
            if ($i != $j && $matrix[$i][$j] > $max) {
                $max = $matrix[$i][$j];
                $pair = [$i, $j];
            }
        }
    }
    return [$max, $pair];
}

// Inisialisasi cluster
$clusters = [];
$clustered = [];
$steps = [];

// Langkah 1: Hanya menampilkan matriks awal
$steps[] = ['matrix' => copyMatrix($similarityMatrix), 'clusters' => [], 'highlight' => null, 'minSimilarity' => findMinSimilarity($similarityMatrix)];

// Fungsi untuk menggabungkan dokumen ke dalam cluster
function addToCluster($doc1, $doc2, &$clusters, &$clustered) {
    if (!isset($clustered[$doc1]) && !isset($clustered[$doc2])) {
        $clusters[] = [$doc1, $doc2];
        $clustered[$doc1] = true;
        $clustered[$doc2] = true;
    } elseif (isset($clustered[$doc1]) && !isset($clustered[$doc2])) {
        foreach ($clusters as &$cluster) {
            if (in_array($doc1, $cluster)) {
                $cluster[] = $doc2;
                $clustered[$doc2] = true;
                break;
            }
        }
    } elseif (!isset($clustered[$doc1]) && isset($clustered[$doc2])) {
        foreach ($clusters as &$cluster) {
            if (in_array($doc2, $cluster)) {
                $cluster[] = $doc1;
                $clustered[$doc1] = true;
                break;
            }
        }
    }
}

// Langkah-langkah pembentukan cluster
while (true) {
    list($maxSimilarity, $pair) = findMaxSimilarityPair($similarityMatrix);
    if (empty($pair)) break;
    
    list($doc1, $doc2) = $pair;
    $minSimilarity = findMinSimilarity($similarityMatrix);

    addToCluster($doc1, $doc2, $clusters, $clustered);
    
    $similarityMatrix[$doc1][$doc2] = 0;
    $similarityMatrix[$doc2][$doc1] = 0;
    
    // Simpan langkah saat ini
    $steps[] = ['matrix' => copyMatrix($similarityMatrix), 'clusters' => $clusters, 'highlight' => [$doc1, $doc2], 'minSimilarity' => $minSimilarity];
}

// Membentuk cluster baru untuk dokumen yang belum termasuk dalam cluster manapun
$size = count($similarityMatrix);
for ($i = 0; $i < $size; $i++) {
    if (!isset($clustered[$i])) {
        $clusters[] = [$i];
        $steps[] = ['matrix' => copyMatrix($similarityMatrix), 'clusters' => $clusters, 'highlight' => null];
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matrik Maksimum Capturing</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <style>
        .highlight {
            color: red;
        }
    </style>
</head>
<body>
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <div class="container">
                     <h5 class="mb-4">Sample Data Tweet</h5>
                         <table class="table table-bordered">
                             <thead>
                                <tr>
                                    <th>Dokumen</th>
                                    <th>Tweet</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($data as $item): ?>
                                    <tr>
                                        <td><?php echo $item['dokumen']; ?></td>
                                        <td><?php echo $item['tweet']; ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
        
        <button id="show-steps" class="btn btn-primary mb-3">Tampilkan Langkah-langkah Pembentukan Cluster</button>
        
        <div id="steps-container" style="display:none;">
            <?php foreach ($steps as $index => $step): ?>
                <h4 class="mt-4">Langkah <?php echo $index + 1; ?>: <?php echo $index == 0 ? "Matrik A" : "Cluster"; ?></h4>
                <div class="row">
                    <div class="col-md-6">
                        <table class="table table-bordered table-sm">
                            <thead>
                                <tr>
                                    <th>Dokumen</th>
                                    <?php for ($i = 0; $i < $size; $i++): ?>
                                        <th><?php echo "D" . ($i + 1); ?></th>
                                    <?php endfor; ?>
                                </tr>
                            </thead>
                            <tbody>
                                <?php for ($i = 0; $i < $size; $i++): ?>
                                    <tr>
                                        <td><?php echo "D" . ($i + 1); ?></td>
                                        <?php for ($j = 0; $j < $size; $j++): ?>
                                            <td <?php if ($step['highlight'] && (($i == $step['highlight'][0] && $j == $step['highlight'][1]) || ($i == $step['highlight'][1] && $j == $step['highlight'][0]))): ?> class="highlight" <?php endif; ?>>
                                                <?php echo $step['matrix'][$i][$j]; ?>
                                            </td>
                                        <?php endfor; ?>
                                    </tr>
                                <?php endfor; ?>
                            </tbody>
                        </table>
                        <?php if ($step['minSimilarity'] !== null && $index > 0): ?>
                            <p>Nilai similarity minimum: <?php echo $step['minSimilarity']; ?></p>
                        <?php endif; ?>
                    </div>
                    <div class="col-md-6">
                        <h4>Clusters:</h4>
                        <ul>
                            <?php foreach ($step['clusters'] as $cluster): ?>
                                <li>[<?php echo implode(", ", array_map(function($doc) { return "D" . ($doc + 1); }, $cluster)); ?>]</li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
    </div>
</div>
</div>
</div>

<script>
    document.getElementById('show-steps').addEventListener('click', function() {
        var stepsContainer = document.getElementById('steps-container');
        if (stepsContainer.style.display === 'none') {
            stepsContainer.style.display = 'block';
            this.textContent = 'Sembunyikan Langkah-langkah Pembentukan Cluster';
        } else {
            stepsContainer.style.display = 'none';
            this.textContent = 'Tampilkan Langkah-langkah Pembentukan Cluster';
        }
    });
</script>
</body>
</html>

<?php
$title = "maxcapturing";
$page_title = "Matrik Maksimum Capturing";
$content = ob_get_clean();
include 'layout.php';
?>
