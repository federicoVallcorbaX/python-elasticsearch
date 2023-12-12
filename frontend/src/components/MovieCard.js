import {useState} from 'react'

import "./components.css"

export const MovieCard = ({title, overview, score, posterPath}) => {
  const [showDescription, setShowDescription] = useState(false);

  return (
    <>
      <div className="movie-card" onClick={() => setShowDescription(true)}>
        <p>{title}</p>
        <img
          height="300px"
          alt=""
          src={`https://image.tmdb.org/t/p/w500${posterPath}`}
        />
        <p>Score: {score.toFixed(3)} &#9733;</p>
      </div>
      {showDescription && (
        <div className="movie-description-modal">
          <div className="x-icon" onClick={() => setShowDescription(false)}>
            &#10006;
          </div>
          <h2 style={{marginBottom: '0px'}}>{title}</h2>
          <p>{overview}</p>
        </div>
      )}
  </>
  )
}
