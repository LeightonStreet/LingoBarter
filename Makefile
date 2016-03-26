.PHONY: run shell test clean

run:
	python lingo.py runserver --reloader --debug

shell:
	python lingo.py shell

test:
	LINGOBARTER_MODE=test py.test --cov=lingobarter -l --tb=long --maxfail=1 lingobarter/

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;