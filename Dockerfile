COPY bot.py .
COPY bot.session .
COPY dbapi.py .
COPY funcs.py .
COPY errors.py .
RUN "bot.py"