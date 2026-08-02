export default function EmptyState({ message = "No hay datos disponibles" }) {
  return (
    <div className="text-center py-12 text-gray-400 text-sm">{message}</div>
  );
}