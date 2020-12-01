window.onload = () => {

    const socket = io('http://localhost:5000');

    socket.on('connect', () => {
        socket.on('connection_established', (message) => {
            console.log(message);
        })
    })

    const body = document.getElementsByTagName('body')[0];

    const sendKeyPressEvent = (event) => {
        const keyPressed = event.key;
        socket.emit("keyPress", { data: keyPressed });
    }

    const sendClickEvent = (event) => {
        const clickOffset = {
            xOffset: event.clientX,
            yOffset: event.clientY,
        };
        socket.emit("click", { data: clickOffset });
    }

    const sendScrollEvent = (event) => {
        const scrollLeft = (window.pageXOffset !== undefined) ? window.pageXOffset : (document.documentElement || document.body.parentNode || document.body).scrollLeft;
        const scrollTop = (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop;
        const scrollOffset = {
            xOffset: scrollLeft,
            yOffset: scrollTop,
        };
        socket.emit("scroll", { data: scrollOffset })
    }

    body.addEventListener('click', sendClickEvent);
    body.addEventListener('keypress', sendKeyPressEvent);
    window.onscroll = () => sendScrollEvent();
}