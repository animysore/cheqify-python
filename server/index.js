function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    var apiKey = " ";
    xmlHttp.open( "GET", "http://localhost:8000", false ); 
    xmlHttp.send();
    return xmlHttp.responseText;
}