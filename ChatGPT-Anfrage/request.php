<?php
require_once 'db_connect.php'; // Ersetzen durch eigene Konfiguration
session_start();

// Überprüfen, ob die Teilnehmer-ID in der Session vorhanden ist
if (!isset($_SESSION['participant_id'])) {
    die("Teilnehmer-ID fehlt in der Session.");
}

$participant_id = $_SESSION['participant_id'];

function generateMoviePrompt($movieIdsString, $conn)
{
    // Die Movie-IDs, die durch Kommas getrennt sind, in ein Array umwandeln
    $movieIds = explode(',', $movieIdsString);

    // Überprüfen, ob genau fünf IDs bereitgestellt wurden
    if (count($movieIds) !== 6) {
        return "Bitte genau sechs Movie-IDs angeben.";
    }

    $prompt = "I like these 6 movies the most: ";

    foreach ($movieIds as $id) {
        // SQL-Abfrage, um Genre und Tags für jede Movie-ID zu holen
        $query = "SELECT title, genres, GROUP_CONCAT(tag SEPARATOR ', ') AS tags FROM movies LEFT JOIN tags ON movies.movieId = tags.movieId WHERE movies.movieId = ? GROUP BY movies.movieId";
        $stmt = $conn->prepare($query);
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $title = $row['title'];
            $genres = $row['genres'];
            $tags = $row['tags'];

            $prompt .= "Title: $title; Genres: $genres";
            if (!empty($tags)) {
                $prompt .= "; Tags: $tags";
            }
            $prompt .= "; ";
        } else {
            $prompt .= "Keine Details für Movie-ID '$id' gefunden; ";
        }
    }

    return $prompt;
}

function getMovieRecommendations($prompt, $conn)
{
    $apiKey = "XXXXXXXXXXXXXXXXXXX"; // ersetzen durch eigenes Modell

    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, "https://api.openai.com/v1/chat/completions");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
        "model" => "ft:gpt-3.5-turbo-1106:personal:thesis:8zR1yPVV",
        "messages" => [
            [
                "role" => "system",
                "content" => "This chatbot gives personalized movie recommendations based on users' favourite movies. The model only outputs 4 different movie suggestions without further information separated by semicolon. There is no extra text or even a word then the titles with the year in brackets. No intro or outro text either. Never anything like: Based on your favorite films, here are some personalized recommendations for you or Enjoy exploring these films!. Dont't show the Tags or the Genre in the answer and don't start with Title:. Just the movie XYZ (2012);ZSD (2020); and so on. So not simply movie XYZ part 1; movie XYZ part 2; movie XYZ part 3; movie ZXY."
            ],
            [
                "role" => "user",
                "content" => $prompt
            ]
        ],
        "temperature" => 1,
        "max_tokens" => 1707,
        "top_p" => 1,
        "frequency_penalty" => 0,
        "presence_penalty" => 0
    ]));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        "Content-Type: application/json",
        "Authorization: Bearer " . $apiKey
    ]);

    $result = curl_exec($ch);
    $httpStatusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if (curl_errno($ch)) {
        echo 'Fehler bei der Anfrage: ' . curl_error($ch);
    } elseif ($httpStatusCode != 200) {
        echo 'API-Fehler: HTTP-Statuscode ' . $httpStatusCode . ' erhalten. Antwort: ' . $result;
    } else {
        // Verarbeiten der Antwort, um Filmempfehlungen zu extrahieren
        $response = json_decode($result, true);
        $recommendedMovies = extractMovieTitles($response);
        // Datenbankabfrage, um Details zu den empfohlenen Filmen zu erhalten
        return $recommendedMovies;
    }

    curl_close($ch);
}


function extractMovieTitles($response)
{
    // Extrahieren der Filmtitel aus der Antwort
    $movies = [];
    $content = $response['choices'][0]['message']['content'];
    $titles = explode(";", $content);
    foreach ($titles as $title) {
        $title = trim($title);
        if (!empty($title)) {
            $movies[] = $title;
        }
    }
    return $movies;
}

function getMovieDetailsFromDB($movieTitles, $conn)
{

    $moviesDetails = [];
    foreach ($movieTitles as $title) {
        // SQL-Abfrage, um Details des Films zu bekommen, basierend auf der größten Übereinstimmung
        $query = "SELECT movieId FROM movies WHERE title LIKE CONCAT('%', ?, '%') ORDER BY CHAR_LENGTH(title) - CHAR_LENGTH(?) LIMIT 1";
        $stmt = $conn->prepare($query);
        $stmt->bind_param("ss", $title, $title);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($result->num_rows > 0) {
            $movieDetails = $result->fetch_assoc();
            $moviesDetails[] = $movieDetails;
        } else {

        }
    }
    return $moviesDetails;
}

function getUniqueMovieRecommendations($inputMoviesString, $conn)
{
    $maxAttempts = 10;
    $attemptCount = 0;
    $uniqueRecommendations = [];
    if (!$inputMoviesString) {
        error_log("getUniqueMovieRecommendations wurde ohne Eingabe aufgerufen.");
        return [
            'error' => "Kein Eingabestring für Filme bereitgestellt.",
            'attempts' => $attemptCount,
            'recommendations' => $uniqueRecommendations
        ];
    }
    $inputMovies = explode(",", $inputMoviesString);
    if (empty($inputMovies)) {
        error_log("Fehler beim Explodieren von inputMoviesString: $inputMoviesString");
        return [
            'error' => "Eingabestring konnte nicht in ein Array umgewandelt werden.",
            'attempts' => $attemptCount,
            'recommendations' => $uniqueRecommendations
        ];
    }
    $prompt = generateMoviePrompt($inputMoviesString, $conn);
    while (count($uniqueRecommendations) < 4 && $attemptCount < $maxAttempts) {
        $attemptCount++;
        $result1 = getMovieRecommendations($prompt, $conn);
        if (!$result1) {
            error_log("getMovieRecommendations lieferte keinen Wert für prompt: $prompt");
            continue;
        }
        $movieDetails = getMovieDetailsFromDB($result1, $conn);
        if (empty($movieDetails)) {
            error_log("getMovieDetailsFromDB lieferte keine Details für Filme: " . implode(", ", $result1));
            continue;
        }
        foreach ($movieDetails as $movie) {
            if (!in_array($movie['movieId'], $inputMovies) && !in_array($movie['movieId'], $uniqueRecommendations) && count($uniqueRecommendations) < 4) {
                $uniqueRecommendations[] = $movie['movieId'];
            }
        }
    }

    return [
        'error' => null,
        'attempts' => $attemptCount,
        'recommendations' => $uniqueRecommendations
    ];
}

// Datenbankabfrage, um chosen_movie_ids zu erhalten
$sql = "SELECT chosen_movie_ids FROM fav_movies WHERE participant_id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param('s', $participant_id);
$stmt->execute();
$result = $stmt->get_result();
if ($result->num_rows == 0) {
    die("Keine Daten für die Teilnehmer-ID gefunden.");
}
$row = $result->fetch_assoc();
$chosen_movie_ids = json_decode($row['chosen_movie_ids'], true);
$movie_ids = array_map('intval', $chosen_movie_ids);
$movieIdsString = implode(",", $movie_ids);
$resultend = getUniqueMovieRecommendations($movieIdsString, $conn);
$recommended_movie_ids = $resultend['recommendations'];

$movie_details = [];

foreach ($recommended_movie_ids as $movieId) {
    $sql = "SELECT m.movieId, m.title, m.genres, l.imdbId, gt.title_ger, e.description, e.poster_path
            FROM movies m 
            JOIN links l ON m.movieId = l.movieId 
            LEFT JOIN ger_title gt ON m.movieId = gt.movieId
            LEFT JOIN extra_info e ON m.movieId = e.movieId
            WHERE m.movieId = ?";
    $stmt = $conn->prepare($sql);
    if ($stmt) {
        $stmt->bind_param("i", $movieId);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($result->num_rows > 0) {
            array_push($movie_details, $result->fetch_assoc());
        } else {
            echo "Kein Film gefunden für ID: $movieId<br>"; // Hinweis, falls kein Film gefunden wird
        }
        $stmt->close();
    } else {
        echo "Fehler bei der Vorbereitung des Statements für Film-ID: $movieId<br>"; // Fehlerbehandlung
    }
}

?>