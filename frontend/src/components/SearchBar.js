import { useState } from "react";

import "./components.css"

export const SearchBar = ({ fetchMovies, suggestion, suggestionHtml }) => {
  const [autocompleteOptions, setAutocompleteOptions] = useState([]);
  const [query, setQuery] = useState('');

  const fetchAutoComplete = async (text) => {
    const response = await fetch(`http://localhost:8000/api/completion?query=${text}`);
    const response_json = await response.json();
    setAutocompleteOptions(response_json.suggestions);
  }

  const handleInputChange = (e) => {
    const text = e.target.value;
    setQuery(text);
    if (text) fetchAutoComplete(text);
  }

  const onSubmit = (e) => {
    e.preventDefault();
    fetchMovies(
      query,
      e.target.elements.semantic.checked,
      e.target.elements.suggestions.checked,
      e.target.elements.embedding.value,
    );
  }

  const handleSuggestionClick = (e) => {
    setQuery(suggestion);
    const form = document.getElementById("form-id")
    form.requestSubmit();
  }

  return (
    <section className="search-bar">
      <form
        id="form-id"
        onSubmit={onSubmit}>
        <input
          type="text"
          autoComplete="off"
          list="search-options"
          className="search-field"
          placeholder="Search for a movie"
          name="search"
          onChange={handleInputChange}
          value={query}
        />
        <datalist id="search-options">
          {autocompleteOptions.map((option) => (
            <option key={option} value={option} />
          ))}
        </datalist>
        <label className="check-box-label">
          Include Suggestions
          <input type="checkbox" className="check-box" name="suggestions" />
        </label>
        <label className="check-box-label">
          Semantic search
          <input type="checkbox" className="check-box" name="semantic" />
        </label>
        <label className="check-box-label">
          Embedding Type
          <select className="select" name="embedding">
            <option value="symmetric">Sbert 1</option>
            <option value="asymmetric">Sbert 2</option>
            <option value="openai">OpenAi</option>
          </select>
        </label>

        {!!suggestion && (
        <p className="did-you-mean">
          Did you mean&nbsp;
          <button
            type="button"
            onClick={handleSuggestionClick}
            dangerouslySetInnerHTML={{__html:suggestionHtml}}
          />
          &nbsp;?
        </p>
      )}
      </form>
    </section>
  )
}
