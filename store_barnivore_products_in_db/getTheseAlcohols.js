var request = require('request');
var pg = require('pg');
require("./secretConstants");
var beerURL = "http://www.barnivore.com/beer.json";
var wineURL = "http://barnivore.com/wine.json";
var liquorURL = "http://barnivore.com/liquor.json";
var companyURLs = [];
var products = [];
var insertCompanyQueryString = 'INSERT INTO barnivore_company (barnivore_id, barnivore_company_name, barnivore_country) VALUES ($1, $2, $3)';
var insertProductQueryString = 'INSERT INTO barnivore_product (barnivore_id, barnivore_company_id, barnivore_product_name, barnivore_status, barnivore_created_on, barnivore_updated_on, barnivore_booze_type, barnivore_country) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)';
getCompanyJson([beerURL, wineURL, liquorURL]);

/**
	This is a script I run to update a postgres database with fresh information from barnivore.
	I only do this so I don't spam them with JSON requests. So far, I've run this like once every 6 months. 

	BTW barnivore are freaking awesome for making this info so easily usable.

	TODO: write a more elegant solution to this which I can put in a bash script on a server and get new updates automatically
**/

function getCompanyJson(urls) {
	var url = urls.pop();
	request({
		url: url,
		json: true
	}, function (error, response, body) {
		if (error) console.log(error);
		if (!error && response.statusCode === 200) {
			console.log(url + " loaded!");
			for (var i = 0; i < body.length; i++) {
				var insertQueryValues = [body[i].company.id, body[i].company.company_name, body[i].company.country];
				runQuery(insertCompanyQueryString, insertQueryValues);
				companyURLs.push('http://www.barnivore.com/company/' + body[i].company.id + '.json');
			}
			if (urls.length === 0) {
				getProductJson(companyURLs);
				//console.log("done");
			} else {
				getCompanyJson(urls);
			}
		}
	});
}

function getProductJson(urls) {
	var url = urls.pop();
	request({
		url: url,
		json: true
	}, function (error, response, body) {
		if (error) console.log(error);
		if (!error && response.statusCode === 200) {
			console.log(url + " loaded!");
			for (var i = 0; i < body.company.products.length; i++) {
				var insertQueryValues = [
					body.company.products[i].id,
					body.company.products[i].company_id, 
					body.company.products[i].product_name, 
					body.company.products[i].status, 
					body.company.products[i].created_on, 
					body.company.products[i].updated_on, 
					body.company.products[i].booze_type, 
					body.company.products[i].country
				];
				runQuery(insertProductQueryString, insertQueryValues);
			}
			
			products.push(body.company.products);
			if (urls.length === 0) {
				console.log("Product load complete.")
				console.log(products);
			} else {
				getProductJson(urls);
			}
		}
	});
}


function runQuery(queryString, queryValues) {
    pg.connect(DB_CONNECT_STRING, function(err, client, done) {
        if(err) {
            return console.error('error fetching client from pool', err);
        }
		client.query(queryString, queryValues, function(err, result) {
			//call `done()` to release the client back to the pool
			done();

			if(err) {
				return console.error('error running query', err);
			}
			console.log(result.rows);
			
		});
	});
}
   