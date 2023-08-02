// ==UserScript==
// @name         FuckBiliLoginWindow
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://www.bilibili.com/video/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=greasyfork.org
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const sendPlay = () => {
        let b = document.querySelector('.bpx-player-ctrl-play');
        if(!b) return;
        b.click();
    }

    window.addEventListener('load', () => {
        setInterval(() => {
            let c = document.querySelector('.bpx-player-state-play')
            if(window.getComputedStyle(c)['display'] != 'none'){
                sendPlay()
            }
            let a = document.querySelector('.bili-mini-mask');
            if(!a) return;
            a.remove();
            sendPlay()
        }, 300)
    })
})();
