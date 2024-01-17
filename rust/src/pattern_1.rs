
/*
Problem Link: https://www.codingninjas.com/studio/problems/n-forest_6570177?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems
*/

pub fn print_pattern(N: i32){
    for i in 1..=N {
        for j in 1..=N {
            print!("*");
        }
        println!();
    }
}