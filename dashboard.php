<?php
ob_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $title; ?></title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
<div class="container mt-4 mb-4">
    <div class="row">
        <div class="col-md-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <h2 id="dataAsliCount" class="card-title">0</h2>
                    <p class="card-text">Data Asli</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <h2 id="dataBersihCount" class="card-title">0</h2>
                    <p class="card-text">Data Bersih</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <h2 id="dataModelCount" class="card-title">0</h2>
                    <p class="card-text">Data Model</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <h2 id="clusterCount" class="card-title">0</h2>
                    <p class="card-text">Cluster Terbentuk</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
    function fetchData() {
        $.ajax({
            url: 'proses_dash.php?action=getData',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                $('#dataAsliCount').text(data.data_asli);
                $('#dataBersihCount').text(data.data_bersih);
                $('#dataModelCount').text(data.data_model);
                $('#clusterCount').text(data.cluster_terbentuk);
            }
        });
    }

    $(document).ready(function() {
        fetchData();
    });
</script>
</body>
</html>

<?php
$title = "Dashboard";
$page_title = "Dashboard";
$content = ob_get_clean();
include 'layout.php';
?>
