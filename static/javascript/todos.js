const handleBack = () => {
  // Redirect to the Todos page
  window.location.href = '/todos';
};

const toggleCompleted = async todo => {
  const { id, title, completed } = JSON.parse(todo);

  try {
    const response = await fetch(`/todos/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id, title, completed: !completed })
    });

    const data = await response.json();

    if (response.status === 200) {
      // Reload the page
      window.location.reload();
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error(error.message);
  }
};
