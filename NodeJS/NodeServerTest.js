const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/AffectSocket';

//Callback for Socket

const handler = (socket) =>
{
    socket.on('data',(bytes) =>
    {
        const msg = bytes.toString();

        console.log(msg);

        return socket.write('Yo faggot');
    });
};

fs.unlink(
    socketPath,
    // Create the server, give it our callback handler and listen at the path
  () => net.createServer(handler).listen(socketPath)
);