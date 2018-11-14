const onvif = require('node-onvif');
var sourceFile = require('./config.js');

// Create an OnvifDevice object
let device = new onvif.OnvifDevice({
    xaddr: sourceFile.xaddr,
    user : sourceFile.user,
    pass : sourceFile.pass
});

//'ProfileToken': this.current_profile['token'],

device.init().then(() => {
    // Move the camera
    // return device.GotoPreset({
    //     'ProfileToken': this.current_profile['token'],
    //     'speed': {
    //         x: -1.0, // Speed of pan (in the range of -1.0 to 1.0)
    //         y: 0.0, // Speed of tilt (in the range of -1.0 to 1.0)
    //         z: 0.0  // Speed of zoom (in the range of -1.0 to 1.0)
    //     },
    //     'timeout': 1 // seconds
    // });


    let params = {
        'ProfileToken': this.current_profile['token'],
        'PresetToken' : '4',
        'Speed'       : {'x': 1, 'y': 1, 'z': 1}
    };

    device.services.ptz.gotoPreset(params).then((result) => {
        console.log(JSON.stringify(result['data'], null, '  '));
    }).catch((error) => {
        console.error(error);
    });



}).then(() => {
    console.log('Turning Left!');
    // Stop to the PTZ in 2 seconds  2000
    setTimeout(() => {
        device.ptzStop().then(() => {
            console.log('Movement Stopped!');
        }).catch((error) => {
            console.error(error);
        });
    }, 2000);
}).catch((error) => {
    console.error(error);
});