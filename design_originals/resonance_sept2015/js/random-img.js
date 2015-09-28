

/*
Random Image Script- By JavaScript Kit (http://www.javascriptkit.com) 
Over 400+ free JavaScripts here!
Keep this notice intact please
*/

function random_imglink(){
var myimages=new Array()
//specify random images below. You can have as many as you wish
myimages[1]="/images/semicolon.jpg"
myimages[2]="/images/header.jpg"
myimages[3]="/images/poetry.jpg"
myimages[4]="/images/No-9-cover.jpg"
myimages[5]="/images/comics.jpg"


var ry=Math.floor(Math.random()*myimages.length)
if (ry==0)
ry=1
document.write('<img src="'+myimages[ry]+'" border=0>')
}


