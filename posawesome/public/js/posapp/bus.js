const evntBus = new Vue();

origEmitter = evntBus.$emit;

evntBus.$emit = function() {
    console.log('Event emitted: ' + arguments[0]);
    origEmitter.apply(this, arguments);
}

export { evntBus };