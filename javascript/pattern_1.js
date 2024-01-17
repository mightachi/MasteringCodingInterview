/*
Problem Link: https://www.codingninjas.com/studio/problems/n-forest_6570177?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems
*/

function printPattern(N) {
    for(let i=0; i<N;i++){
        for(let j=0; j<N;j++){
            process.stdout.write("*");
        }
        console.log()
    }
}

printPattern(3)