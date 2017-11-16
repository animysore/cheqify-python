function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    var apiKey = " ";
    xmlHttp.open( "GET", "http://localhost:5000", false ); 
    xmlHttp.send();
    return xmlHttp.responseText;
}