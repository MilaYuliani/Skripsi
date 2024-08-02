<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8" />
    <title> web skripsi mila </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta content="A fully featured admin theme which can be used to build CRM, CMS, etc." name="description" />
    <meta content="Coderthemes" name="author" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <!-- App favicon -->
    <link rel="shortcut icon" href="assets/images/favicon.ico">

    <!-- App css -->

    <link href="assets/css/app.min.css" rel="stylesheet" type="text/css" id="app-style" />


    <!-- third party css -->
    <link href="assets/libs/datatables.net-bs5/css/dataTables.bootstrap5.min.css" rel="stylesheet" type="text/css" />
    <link href="assets/libs/datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css" rel="stylesheet"
        type="text/css" />
    <link href="assets/libs/datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css" rel="stylesheet"
        type="text/css" />
    <link href="assets/libs/datatables.net-select-bs5/css//select.bootstrap5.min.css" rel="stylesheet"
        type="text/css" />
    <!-- third party css end -->


    <!-- icons -->
    <link href="assets/css/icons.min.css" rel="stylesheet" type="text/css" />

</head>

<!-- body start -->

<body class="loading" data-layout-color="light" data-layout-mode="default" data-layout-size="fluid"
    data-topbar-color="light" data-leftbar-position="fixed" data-leftbar-color="light" data-leftbar-size='default'
    data-sidebar-user='true'>

    <header>
        <?php include 'header.php'; ?>
    </header>

    <!-- Begin page -->
    <div id="wrapper">
        <!-- end Topbar -->
        <!-- ========== Left Sidebar Start ========== -->
        <div class="left-side-menu">
            <!-- User box -->
            <div class="user-box text-center">

                <img src="assets/images/logobl.jpg" alt="user-img" title="Mat Helme"
                    class="rounded-circle img-thumbnail avatar-md">
                <div class="dropdown">
                    <div class="dropdown-menu user-pro-dropdown">

                    </div>
                </div>

                <h5 class="text-muted left-user-info">Web Klasifikasi & NER </h5>
            </div>

            <!--- Sidemenu -->
            <div id="sidebar-menu">

                <ul id="side-menu">
                    <li class="menu-title"></li>

                    <li>
                        <a href="dashboard">
                            <i class="fe-home"></i>
                            <span> Dashboard </span>
                        </a>
                    </li>


                    <li>
                        <a href="crawling">
                            <i class="fe-file"></i>
                            <span>Import Data </span>
                        </a>
                    </li>

                    <li>
                        <a href="prepocesing">
                            <i class="fe-database"></i>
                            <span> Prepocesing </span>
                        </a>
                    </li>
                    <li>
                        <a href="#email" data-bs-toggle="collapse">
                            <i class="fe-pie-chart"></i>
                            <span> Clustering</span>
                            <span class="menu-arrow"></span>
                            </a>
                            <div class="collapse" id="email">
                                <ul class="nav-second-level">
                                    <li>
                                        <a href="clustering">Jaccard Similarity</a>
                                    </li>
                                    <li>
                                        <a href="maxcapturing">Maksimum Capturing</a>
                                    </li>
                                </ul>
                            </div>
                        </li>
                        <li>
                        <li>
                            <a href="hybrid_tfidf">
                                 <i class="fe-book-open"></i>
                                <span>Kalimat Utama</span>
                            </a>
                        </li>
                        <li>
                            <a href="#sidebarTasks" data-bs-toggle="collapse">
                                <i class="fe-folder"></i>
                                <span> NER </span>
                                <span class="menu-arrow"></span>
                            </a>
                            <div class="collapse" id="sidebarTasks">
                                <ul class="nav-second-level">
                                    <li>
                                        <a href="ner_rule">Rule based</a>
                                    </li>
                                     <!-- <li>
                                    <a href="ner_testing">Testing</a>
                                    </li> -->
                                </ul>
                            </div>
                        </li>
                    <li>
                        <a href="pengujian">
                            <i class="fe-check-square"></i>
                            <span> Pengujian </span>
                        </a>
                    </li>
                    <li>
                        <a href="visual2">
                            <i class="fe-bar-chart-2"></i>
                            <span> Visualisasi</span>
                        </a>
                    </li>
                </ul>

            </div>
            <!-- End Sidebar -->

            <div class="clearfix"></div>

        </div>
        <!-- Sidebar -left -->

    </div>
    <!-- Left Sidebar End -->

    <!-- ============================================================== -->
    <!-- Start Page Content here -->
    <!-- ============================================================== -->

    <div class="content-page">
        <div class="content">

            <!-- Start Content-->
            <div class="container-fluid">
                <?php echo $content; ?>
            </div> <!-- container-fluid -->

        </div> <!-- content -->

        <!-- Footer Start -->
        <footer class="footer">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-6">
                        <script>document.write(new Date().getFullYear())</script> &copy; web by <a href="https://www.linkedin.com/in/mila-yuliani-67b2ba218/">Mila
                            Yuliani</a>
                    </div>
                    <div class="col-md-6">
                        <div class="text-md-end footer-links d-none d-sm-block">
                            <a href="https://www.instagram.com/_mila.yyy/">Contact Us</a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
        <!-- end Footer -->

    </div>
    <!-- ============================================================== -->
    <!-- End Page content -->
    <!-- ============================================================== -->


    </div>
    <!-- END wrapper -->

    <!-- Right Sidebar -->

    <!-- /Right-bar -->

    <!-- Right bar overlay-->
    <div class="rightbar-overlay"></div>

    <!-- Vendor -->
    <script src="assets/libs/jquery/jquery.min.js"></script>
    <script src="assets/libs/bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="assets/libs/simplebar/simplebar.min.js"></script>
    <script src="assets/libs/node-waves/waves.min.js"></script>
    <script src="assets/libs/waypoints/lib/jquery.waypoints.min.js"></script>
    <script src="assets/libs/jquery.counterup/jquery.counterup.min.js"></script>
    <script src="assets/libs/feather-icons/feather.min.js"></script>

    <!-- knob plugin -->
    <script src="assets/libs/jquery-knob/jquery.knob.min.js"></script>

    <!--Morris Chart-->
    <script src="assets/libs/morris.js06/morris.min.js"></script>
    <script src="assets/libs/raphael/raphael.min.js"></script>

    <!-- Datatables init -->
    <script src="assets/js/pages/datatables.init.js"></script>

    <!-- Dashboar init js-->
    <script src="assets/js/pages/dashboard.init.js"></script>

    <!-- App js-->
    <script src="assets/js/app.min.js"></script>

    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>

<!-- DataTables CSS -->
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">

<!-- DataTables JS -->
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>

<script src="path/to/your/js/jquery.min.js"></script>
<script src="path/to/your/js/bootstrap.bundle.min.js"></script>


<!-- Initialize DataTables -->
<script>
$(document).ready(function() {
    $('#datatable-pembobotan').DataTable();
    $('#datatable-kalimat-utama').DataTable();
});
</script>

</body>
</html