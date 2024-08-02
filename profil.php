<?php
ob_start();
?>
    <div class="row">
    <div class="container mt-4 mb-4">
        <div class="col-md-12">
            <div class="card mx-auto" style="max-width: 900px;">
                <div class="card-header">
                    My Profile
                </div>
                <div class="card-body">
                    <!-- Konten My Account -->
                    <div class="row">
                        <div class="col-md-4">
                            <img src="assets/images/logoubl.png" alt="Logo" class="img-fluid">
                        </div>
                        <div class="col-md-8">
                            <h4>KLASTERISASI INFORMASI BENCANA ALAM PADA DATA TWITTER MENGGUNAKAN METODE MAXIMUM CAPTURING DENGAN JACCARD SIMILARITY DAN EKSTRAKSI NAMED ENTITY RECOGNITION (NER) BERBASIS RULE-BASED</h4>
                            <p>Nama: Mila Yuliani</p>
                            <p>NIM: 2011500846</p>
                            <p>Prodi : Teknik Informatika</p>
                            <P>Tahun : 2023/2024</P>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<?php
$title = "My Account";
$page_title = "welcome";
$content = ob_get_clean();
include 'layout.php';
?>
