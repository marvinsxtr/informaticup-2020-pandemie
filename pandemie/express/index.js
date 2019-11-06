let express = require("express");
let app = express();

app.use(express.json({ limit: "2mb" }));
app.post("/", function(request, response) {
	let { round, outcome, error } = request.body
	console.log(`Round: ${round}, outcome: ${outcome}, error: ${error}`);
	response.send({ type: "endRound" });
});
app.listen(50123);
