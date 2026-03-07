export default function CardGridExample() {
  const cards = Array.from({ length: 6 }, (_, i) => ({
    id: i + 1,
    title: `Card ${i + 1}`,
    description: 'This is a responsive card using Tailwind and the provided design tokens.',
  }))
  return (
    <div className="p-8">
      <h1 className="title mb-6 text-center">Responsive Card Grid</h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map(({ id, title, description }) => (
          <div
            key={id}
            className="glass-shine rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-lg dark:border-gray-700 dark:bg-gray-800"
          >
            <h2 className="heading mb-2">{title}</h2>
            <p className="paragraph muted">{description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}