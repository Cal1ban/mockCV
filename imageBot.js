// This example shows how to render pages that perform AJAX calls
// upon page load.
//
// Instead of waiting a fixed amount of time before doing the render,
// we are keeping track of every resource that is loaded.
//
// Once all resources are loaded, we wait a small amount of time
// (resourceWait) in case these resources load other resources.
//
// The page is rendered after a maximum amount of time (maxRenderTime)
// or if no new resources are loaded.
var system = require('system');
var args = system.args;

var resourceWait  = 300,
    maxRenderWait = 1000;

var url = ['http://www.techradar.com/news/phone-and-communications/mobile-phones/best-cheap-smartphones-payg-mobiles-compared-961975','http://cdn.mos.cms.futurecdn.net/oFQn7Z5npUQzDz5Q2fDb8k-970-80.jpg'];
var path = ['/Users/georgeseed/hackathon/images/main_image.jpg','/Users/georgeseed/hackathon/hera_image.png'];
var page          = require('webpage').create(),
    count         = 0,
    forcedRenderTimeout,
    renderTimeout;

page.viewportSize = { width: 1800, height : 1500 };

//ideally would read JSON on this as input

function doRender(localPath) {
  if (localPath == '/Users/georgeseed/hackathon/hero_image.png'){
    console.log('width: '+imageAPI.widthIMG);
    console.log('width: '+imageAPI.heightIMG);
    page.viewportSize = { width: imageAPI.widthIMG , height : imageAPI.heightIMG };
    page.render(localPath);
  }
  else {
    page.render(localPath);
  }
}

page.onResourceRequested = function (req) {
    count += 1;
    console.log('> ' + req.id + ' - ' + req.url);
    clearTimeout(renderTimeout);
};

page.onResourceReceived = function (res) {
    if (!res.stage || res.stage === 'end') {
        count -= 1;
        console.log(res.id + ' ' + res.status + ' - ' + res.url);
        if (count === 0) {
            renderTimeout = setTimeout(doRender, resourceWait);
        }
    }
};

page.onResourceError = function(resourceError) {
  page.reason = resourceError.errorString;
  console.log(page.reason)
    page.reason_url = resourceError.url;
      console.log(page.reason_url)
};

function handle_page(file, localPath){

    page.open(file, function (status) {
      imageAPI = page.evaluate(function() {
      var widthIMG = document.querySelectorAll('img')[0].naturalWidth;
      var heightIMG = document.querySelectorAll('img')[0].naturalHeight;
      return {width:widthIMG,height:heightIMG}
    });

        if (status !== "success") {
            console.log('Unable to load url');
            phantom.exit();
        } else {
            forcedRenderTimeout = setTimeout(function () {
                doRender(localPath,imageAPI);
                next_page();
            }, maxRenderWait);
        }
    });
}

function next_page(){
    var localPath=path.shift();
    var file=url.shift();
    console.log('loading URL: '+file);
    console.log('Saving at: '+localPath);
    if(!file){console.log('NO MORE URLS'); phantom.exit(0);}
    handle_page(file, localPath)
}

next_page();
