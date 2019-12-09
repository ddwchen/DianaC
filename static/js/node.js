var unirest = require("unirest");

var req = unirest("POST", "https://zillowdimashirokovv1.p.rapidapi.com/getRegionChildren.htm");

req.headers({
	"x-rapidapi-host": "ZillowdimashirokovV1.p.rapidapi.com",
	"x-rapidapi-key": "2aae4f3322mshfe9b9b66de4b6e6p16de92jsnfdf57f37cade",
	"content-type": "application/x-www-form-urlencoded"
});

req.form({
	"childtype": [
		"state",
		"city",
		"zipcode",
		"neighborhood",
		"county"
	],
	"zws-Id": "X1-ZWz1hik9d1zthn_799rh"
});

req.end(function (res) {
	if (res.error) throw new Error(res.error);

	console.log(res.body);
});