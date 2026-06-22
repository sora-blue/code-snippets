// ==UserScript==
// @name         FuckBiliLoginWindow
// @namespace    http://tampermonkey.net/
// @version      0.4
// @description  Also fuck Google in the future for promoting DRM-ed Web
// @author       You
// @match        https://www.bilibili.com/video/*
// @match        https://search.bilibili.com/*
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

    const checkAndSendPlay = () => {
        let c = document.querySelector('.bpx-player-state-play')
        if(c && window.getComputedStyle(c)['display'] != 'none'){
            sendPlay()
            return false
        }
        return true
    }

    const waitAndCheck = () => {
        setTimeout(checkAndSendPlay, 500)
    }

    window.addEventListener('load', () => {
        setInterval(() => {
            const targets = ['.login-tip', '.bili-mini-mask', '.bpx-player-toast-wrap']
            for(let i = 0 ; i < targets.length ; i++){
                let a = document.querySelector(targets[i]);
                if(!a) continue;
                a.remove();
                    let interval_id;
                    interval_id = setInterval(() => {
                        if(checkAndSendPlay()){
                            clearInterval(interval_id);
                        }
                    }, 200)
                // while(checkAndSendPlay()){} // 直接把渲染线程卡死了，乐
            }
            // waitAndCheck()
        }, 100) 
    })
})();
