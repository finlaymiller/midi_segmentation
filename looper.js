/* 
	looped playback of all MIDI files in a filesystem
	plays the next midi file with the most similar pitch histogram
*/

// max env variables
inlets = 1;
outlets = 4;

// set up inlets
setinletassist(0, "commands");
// set up outlets
setoutletassist(0, "folder path");
setoutletassist(1, "number of files in folder");
setoutletassist(2, "current file");
setoutletassist(3, "next file");

// globals
var folderPath = "/Users/finlay/Documents/Programming/ssm/data/outputs/time/MIDI4-shifted/";
var metricsPath = "/Users/finlay/Documents/Programming/ssm/data/outputs/midi_metrics.json";	
var currentFile = "";
var nextFile = "";
var metrics = new Dict();
var playedFiles = 0;

metrics.import_json(metricsPath);


function play() {
	var folder = new Folder(folderPath);
	
	outlet(0, folder.pathname);
	outlet(1, folder.count);
	
	folder.reset();
	
	while (playedFiles < folder.count) {
		folder.next();
		var file = new File(folder.pathname + '/' + folder.filename);
		currentFile = folder.filename;
		outlet(2, folder.pathname + '/' + folder.filename);
		post(folder.filename);
		
		post(metrics.getkeys(), "\n");
		
		var phs = getPitchHistograms();
		post(phs);
		var fileMetric = metrics.get(folder.filename);
		
		nextFile = findMostSimilarVector(fileMetric['metrics']['pitch_histogram']);
		outlet(3, nextFile);
		
		markasPlayed(folder.filename);
		playedFiles++;
	}
	
	folder.close();
}

function getPitchHistograms() {
		return metrics.getkeys();
		//	.filter(key => metrics.get(key).played == 0);
		//	.map(key => ({
		//	'name': key,
		//	'metric': metrics.get(key)['metrics']['pitch_histogram'];	
		//}));
}

function findMostSimilarVector(targetVector, vectorArray) {
  var mostSimilarVector = null;
  var highestSimilarity = -1;  // since cosine similarity ranges from -1 to 1

  vectorArray.forEach((vectorData) => {
	post(vectorData);
	
    const { name, vector } = vectorData;
    const similarity = 1 - cosineSimilarity(targetVector, vector);

    if (similarity > highestSimilarity) {
      highestSimilarity = similarity;
      mostSimilarVector = name;
    }
  });

  return mostSimilarVector;
}

function cosineSimilarity(vecA, vecB) {
  var dotProduct = 0.0;
  var normA = 0.0;
  var normB = 0.0;

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }

  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

function markAsPlayed(key) {
	var entry = metrics.get(key);
	
	metrics.set({
		...entry,
		'played': 1;
	})
}