const onvif = require('node-onvif');
var sourceFile = require('./config.js');
var childProcess = require('child_process');
// Create an OnvifDevice object
let device = new onvif.OnvifDevice({
    xaddr: sourceFile.xaddr,
    user : sourceFile.user,
    pass : sourceFile.pass
});

function runScript(scriptPath, callback) {

    // keep track of whether callback has been invoked to prevent multiple invocations
    var invoked = false;

    var process = childProcess.fork(scriptPath);

    // listen for errors as they may prevent the exit event from firing
    process.on('error', function (err) {
        if (invoked) return;
        invoked = true;
        callback(err);
    });

    // execute the callback once the process has finished running
    process.on('exit', function (code) {
        if (invoked) return;
        invoked = true;
        var err = code === 0 ? null : new Error('exit code ' + code);
        callback(err);
    });

}

// Initialize the OnvifDevice object
device.init().then(() => {
    // Move the camera
    return device.ptzMove({
        'speed': {
            x: 1.0, // Speed of pan (in the range of -1.0 to 1.0)
            y: 0.0, // Speed of tilt (in the range of -1.0 to 1.0)
            z: 0.0  // Speed of zoom (in the range of -1.0 to 1.0)
        },
        'timeout': 1 // seconds
    });
}).then(() => {
    console.log('Aud - 1 !');
    //console.log('waited');
}).catch((error) => {
    console.error(error);
});

// Now we can run a script and invoke a callback when complete, e.g.
runScript('./turn_to_lecturer_r.js', function (err) {
    if (err) throw err;
    console.log('finished running child script');
});

//'ProfileToken': this.current_profile['token'],