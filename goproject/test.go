package main

import (
	"os"
	// "bufio"
	// "fmt"
	// "net/http"
	"text/template"
)

func main() {
	// type Inventory struct {
	// 	Material string
	// 	Count    uint
	// }
	// sweaters := Inventory{"wool", 17}
	// tmpl, err := template.New("test").Parse("{{.Count}} items are made of {{.Material}}")
	// if err != nil {
	// 	panic(err)
	// }
	// err = tmpl.Execute(os.Stdout, sweaters)
	// if err != nil {
	// 	panic(err)
	// }
	type Inventory struct {
		Month, Id string
	}
	s := Inventory{"20191001", "0056"}
	url := "https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=csv&date={{.Month}}&stockNo={{.Id}}"
	// url := "date={{.month}} &stockNo= {{.id}}"
	// url := "https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=csv&date={{.}}&stockNo={{.}}"
	tmpl, err := template.New("test").Parse(url)
	if err != nil {
		panic(err)
	}
	err = tmpl.Execute(os.Stdout, s)
	if err != nil {
		panic(err)
	}

	// resp, err := http.Get("http://gobyexample.com")
	// if err != nil {
	//     panic(err)
	// }
	// defer resp.Body.Close()

	// fmt.Println("Response status:", resp.Status)

	// scanner := bufio.NewScanner(resp.Body)
	// for i := 0; scanner.Scan() && i < 5; i++ {
	//     fmt.Println(scanner.Text())
	// }

	// if err := scanner.Err(); err != nil {
	//     panic(err)
	// }
}
