def handler(request):
    return (
        200,
        {"Content-Type": "application/json"},
        '{"status":"ok"}',
    )
