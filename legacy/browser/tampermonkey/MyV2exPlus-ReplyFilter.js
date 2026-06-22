// ==UserScript==
// @name         MyV2exPlus-ReplyFilter
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://v2ex.com/t/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=sora2aoi.com
// @grant        none
// ==/UserScript==

(function () {
    'use strict';
    /* Done within 27min together with New Bing */

    // A cell element
    class Cell {
        constructor(element) {
            this.element = element;
        }

        // like number
        getLikeNumber() {
            const smallFadeElements = this.element.getElementsByClassName("small fade");
            if (smallFadeElements.length < 1) {
                return null;
            }
            if (smallFadeElements[0].childNodes.length < 2) {
                return null;
            }
            const smallFadeText = smallFadeElements[0].childNodes[1].textContent.trim();
            const smallFadeNumber = Number(smallFadeText);
            return isNaN(smallFadeNumber) ? null : smallFadeNumber;
        }

        // No. number
        getNoNumber() {
            const noNumber = this.element.querySelector(".no")
            if(!noNumber){
                return null;
            }
            return Number(noNumber.textContent)
        }


        // hide not so good content by filter
        hideIfLikeNumberLessThan(value) {
            const smallFadeNumber = this.getLikeNumber();
            if ((!smallFadeNumber || smallFadeNumber < value) && Number(value) !== 0) {
                this.element.style.display = "none";
            } else {
                this.element.style.display = "block";
            }
        }
    }

    const CELL_SORT_TYPE_NO = "no"
    const CELL_SORT_TYPE_LIKE = "like"

    const sortCell = (cells, sortType, mainElement) => {
        if(sortType === CELL_SORT_TYPE_NO){
            // sort by reply order (ascending)
            cells.sort((a, b) => {
                // not neat solution, just convenient
                const aNo = Number(a.getNoNumber() || 1024768)
                const bNo = Number(b.getNoNumber() || 1024768)
                if(aNo === bNo){
                    return 0
                }
                if(aNo < bNo){
                    return -1
                }
                return 1
            })
        }else if(sortType === CELL_SORT_TYPE_LIKE){
            // sort by like number (descending)
            cells.sort((a, b) => {
                const aLike = Number(a.getLikeNumber() || 0)
                const bLike = Number(b.getLikeNumber() || 0)
                if (aLike === bLike){
                    return 0
                }
                if (aLike < bLike){
                    return 1
                }
                return -1
            })
        }else{
            return
        }
        // do insert
        const target = mainElement.getElementsByClassName("box")[1].firstElementChild
        for (let j = cells.length - 1; j >= 0; j--) {
            target.insertAdjacentElement('afterend', cells[j].element)
        }

    }

    const arrangeCell = (mainElement, inputElement) => {
        let rawCells = document.getElementsByClassName("cell")
        let cells = []
        for (let rCell of rawCells) {
            const id = rCell.getAttribute('id')
            if (!id) continue
            if (!id.startsWith('r_')) continue
            cells.push(rCell)
        }
        cells = Array.from(cells).map((element) => new Cell(element));
        //
        let likeBar = Number(inputElement.value)
        if (likeBar >= 0) {
            sortCell(cells, CELL_SORT_TYPE_NO, mainElement)
            cells.forEach((cell) => cell.hideIfLikeNumberLessThan(likeBar));
        } else {
            sortCell(cells, CELL_SORT_TYPE_LIKE, mainElement)
        }
    }

    // My code here...
    const main = () => {
        const mainElement = document.getElementById("Main");
        const sep20Elements = mainElement.getElementsByClassName("sep20");
        // add bar
        if (sep20Elements.length >= 2) {
            // separation line
            const sep20Element = document.createElement("div")
            sep20Element.className = "sep20"
            // label
            const labelNode = document.createTextNode("超过这个点赞数才显示，负数排序")
            const labelElement = document.createElement("div")
            labelElement.style.fontSize = "small"
            labelElement.appendChild(labelNode)
            // input like bar
            const inputElement = document.createElement("input");
            inputElement.type = "number";
            inputElement.onchange = (event) => {
                arrangeCell(mainElement, inputElement)
            };
            // insert elements
            const waitingList = [sep20Elements[1], labelElement, inputElement, sep20Element]
            for (let i = 0; i < waitingList.length - 1; i++) {
                waitingList[i].insertAdjacentElement("afterend", waitingList[i + 1])
            }
            // sort once
            arrangeCell(mainElement, inputElement)
        }
    }

    // Add
    window.addEventListener('load', () => {
        setTimeout(main, 100)
    })
})();
