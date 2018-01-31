// establish socket connection
// TODO add server connection info
//const SERVER_ADDRESS = 'localhost:5000'

const SERVER_ADDRESS = '0.0.0.0:5000'
const socket = io(SERVER_ADDRESS);


// vue goodness
let app = new Vue({
    el: '#app',
    data: {
        commands: ''
    },
    computed: {
        // check command validity
        checkCommands() {
            let cmds;
            try {
                cmds = JSON.parse(this.commands);
                // check for easy errors
                let validCommands = ['left', 'right', 'stop'];
                let allValid = cmds.every(cmd => {
                    if (!isNaN(cmd) || validCommands.includes(cmd)) return true;
                });
                return allValid;
            } catch (e) {
                return false;
            }
        }
    },
    methods: {
        submit() {
            let cmds = JSON.parse(this.commands);
            socket.emit('submission', cmds);
            console.log('submitted', cmds);
        }
    }
});
