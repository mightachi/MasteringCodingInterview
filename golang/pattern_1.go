/*
Problem Link: https://www.codingninjas.com/studio/problems/n-forest_6570177?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems
*/

package main

import ("fmt")



func main(){
	printPattern(3)
}

func printPattern(N int){
	for i:=0; i<N; i++ {
		for j:=0; j<N; j++ {
			fmt.Print("*")
		}
		fmt.Println()
	}
}