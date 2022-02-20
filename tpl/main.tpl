<!doctype html>
<html lang="fa">
  <head>
    <title>سامانه‌ی آسان پرداخت</title>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <link href="https://cdn.rawgit.com/rastikerdar/vazir-font/v18.0.0/dist/font-face.css" rel="stylesheet" type="text/css" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <link rel="stylesheet" href="{{index}}/static/style.css">
  </head>
  <body>
    <div class="container" id="indexform">
        <div class="row">
            <div class="col-12 box">
              <form action="{{index}}/request" method="GET">

                <div class="row">
                  <div class="col-md-3"><label>نام و نام خانوادگی</label></div>
                  <div class="col-md-9"><input name="name" class="form-control" required></div>
                </div>
                <div class="row">
                    <div class="col-md-3"><label>آدرس ایمیل</label></div>
                    <div class="col-md-9"><input name="email" type="email" class="form-control" placeholder="نیازی به وارد کردن www نیست" required></div>
                </div>
                <div class="row">
                    <div class="col-md-3"><label>مقدار واریزی</label></div>
                    <div class="col-md-9"><input name="price" class="form-control" placeholder="مبلغ به تومان" required></div>
                </div>
                <div class="row">
                    <div class="col-md-3"><label>توضیحات</label></div>
                    <div class="col-md-9"><input name="description" class="form-control" required></div>
                </div>
                <div class="row" id="fbtn">
                  <div class="col-sm-6">
                      <button type="submit" class="btn btn-success">پرداخت</button>
                  </div>
                  <div class="col-sm-6" id="zptrust">
                    <script>
                        function showZPTrust(){ var thewindow = window.open("https://www.zarinpal.com/webservice/verifyWebsite/"+window.location.hostname, null, "width=656, height=500, scrollbars=no, resizable=no"); }
                    </script>
                    <a href="javascript:showZPTrust();"><span class="btn btn-info">بررسی اعتبار وب سایت</span></a>
                  </div>
                </div>
              </form>
            </div>
        </div>
        <footer>
          طراحی و کدنویسی توسط <a href="https://rasooll.com" target="_blank">رسول صفری</a>
        </footer>
    </div>

    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>