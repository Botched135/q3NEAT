var args = process.argv.slice(2);



var EmpaticaE4 = require('empatica-e4-client');
var dev1 = new EmpaticaE4();

var sensorData = '';
var portNumber  = 755;
var ipAddress   = '192.168.0.15';
var deviceID    = '5F04BC';        //Empatica E4 device ID 
dev1.connect(portNumber ,ipAddress, deviceID, function(data){  
    sensorData = EmpaticaE4.getString(data);
	var replace = sensorData.replace("\r\n"," ");
	replace = replace.replace("\r"," ");
	replace = replace.replace("\n"," ");
	var split = replace.split(" ");
	console.log(sensorData);
	//console.log("\r\n");
});
setTimeout(function() {
    //dev1.subscribe(EmpaticaE4.E4_IBI);
	dev1.subscribe(EmpaticaE4.E4_GSR);
}, 1000);




const port = 3490;
var net = require('net');
var server = net.createServer(function(connection) {
    console.log('client connected');

    connection.on('close', function (){
        console.log('client disconnected');
     });

    connection.on('data', function (data) {
        data = data.toString();
        console.log('client sended the folowing string:'+data);
        connection.write(sensorData);
   });

});


server.listen(port, function () {
    console.log('server is listening');
});