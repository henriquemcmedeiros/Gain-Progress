var passed = false;
function SeeMore() {
    const moreDivs = document.getElementById("more");
    if (passed === false){
        document.getElementById("seeMore").src = "../static/images/seeLess.svg";
        moreDivs.style.display = 'inline';
        passed = true;
    }
    else {
        document.getElementById("seeMore").src = "../static/images/seeMore.svg";
        moreDivs.style.display = 'none';
        passed = false;
    }
}