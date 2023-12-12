import { useState } from 'react';

import './App.css';

import { MovieCard } from './components/MovieCard';
import { SearchBar } from './components/SearchBar';


function App() {
  const [movies, setMovies] = useState([]);
  const [suggestion, setSuggestion] = useState('');
  const [suggestionHtml, setSuggestionHtml] = useState('');

  const fetchMovies = async (query, semantic, suggestions, embeddingType) => {
    const url = new URL('http://localhost:8000/api/movies');
    if (query) url.searchParams.append('search', query);
    if (suggestions) url.searchParams.append('include_suggestions', true);
    if (semantic) {
      url.searchParams.append('semantic_search', true);
      url.searchParams.append('emb_type', embeddingType);
    }
    const response = await fetch(url);
    const response_json = await response.json();
    const movies = response_json.movies.filter((movie) => !!movie.poster_path);
    setMovies(movies);
    setSuggestion(response_json.did_you_mean ?? '');
    setSuggestionHtml(response_json.did_you_mean_html ?? '');
  }

  return (
    <div className="app">
      <header className="app-header">
        <SearchBar fetchMovies={fetchMovies} suggestion={suggestion} suggestionHtml={suggestionHtml} />
      </header>
      <section className="movies-section">
        {movies.map((movie) => (
        <MovieCard
          key={movie.item_id}
          title={movie.title}
          overview={movie.overview}
          score={movie.score}
          posterPath={movie.poster_path}
        />))}
      </section>
    </div>
  );
}

export default App;
