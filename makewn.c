//
// take output from svn log and format it into the
// basics of a whatsnew.txt file
//

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define WRAPLEN	70
#define MAX_GAMES 200

static char *newlist[3][MAX_GAMES];
static int nextnew[3];

int stristr(const char *text, const char *findme)
{
	int searchlen = strlen(findme);
	while (*text != 0)
	{
		int index;
		for (index = 0; index < searchlen && tolower(text[index]) == tolower(findme[index]); index++) ;
		if (index == searchlen)
			return 1;
		text++;
	}
	return 0;
}

void flush_common(char *text, const char *firstprefix, const char *subsprefix)
{
	char *origtext = text;
	char *closebracket;
	char *openbracket;
	const char *prefix;

	// find open/close brackets
	closebracket = strrchr(text, ']');
	openbracket = strrchr(text, '[');

	// wrap the text as needed
	prefix = firstprefix;
	while (strlen(text) > WRAPLEN - strlen(prefix))
	{
		char *end = &text[WRAPLEN - strlen(prefix)];
		char save;
		
		// if this puts us in the middle of the backets, back up
		if (end > openbracket && end < closebracket && text < openbracket)
			end = openbracket;

		// scan backwards until we find a space			
		while (end > text && !isspace(*end))
			end--;
		
		// if that didn't work, scan forward until we find a space or the end
		if (end == text)
		{
			end = &text[WRAPLEN - strlen(prefix)];
			while (*end != 0 && !isspace(*end))
				end++;
		}
		
		// terminate and print
		*end = 0;
		printf("%s%s\n", prefix, text);
		
		// advance and remove spaces
		text = end + 1;
		while (*text != 0 && isspace(*text))
			text++;
		
		// use the subsequent prefix for all other lines
		prefix = subsprefix;
	}
	
	// if there's anything left, print it on its own line
	if (*text != 0)
		printf("%s%s\n", prefix, text);
	
	// kill the text
	*origtext = 0;
}

void flush_paragraph(char *text)
{
	flush_common(text, "", "");
}

void flush_paragraph_newline(char *text)
{
	// if no text output nothing
	if (*text == 0)
		return;
	
	// flush normally and then add an extra CR/LF
	flush_paragraph(text);
	printf("\n");
}

void flush_line(char *text)
{
	// skip past whatever prefixes we originally had
	while (*text != 0 && (*text == '*' || *text == '-' || isspace(*text)))
		*text++ = 0;

	// output the rest	
	flush_common(text, " * ", "    ");
}

void print_list(int index)
{
	int i;
	for (i = 0; i < nextnew[index]; i++)
	{
		char *string = newlist[index][i];
		if (strlen(string) > 70)
		{
			char *middle = strchr(string, '[');
			middle[-1] = 0;
			printf("%s\n  %s\n", string, middle);
		}
		else
			printf("%s\n", string);
	}
}

int main(int argc, char *argv[])
{
	char paragraph[65536];
	char fullbuffer[1024];
	char author[100];
	int revision;
	int numfiles;
	FILE *f;
	int state;
	
	printf("0.xxxxx\n-------\n\n\nMAMETesters Bugs Fixed\n----------------------\n\n\nSource Changes\n--------------\n");

	f = fopen(argv[1], "r");
	state = 0;
	while (fgets(fullbuffer, sizeof(fullbuffer), f) != NULL)
	{
		char *buffer = fullbuffer;
		char *end = fullbuffer + strlen(fullbuffer) - 1;
		int spaces_removed = 0;
		
		// trim off spaces
		while (*buffer != 0 && isspace(*buffer))
		{
			buffer++;
			spaces_removed++;
		}
		while (end > buffer && isspace(*end))
			*end-- = 0;
	
		// long dashed line always ends previous state
		if (strncmp(buffer, "----------------------------------------------------------------------", 70) == 0)
		{
			flush_paragraph_newline(paragraph);
			state = 0;
			numfiles = 0;
			paragraph[0] = 0;
			continue;
		}
		
		// state 0 expects a revision and author
		if (state == 0)
		{
			if (sscanf(buffer, "r%d | %s |", &revision, author) == 2)
				printf("Revision %d by %s\n", revision, author);
			else
				printf("Unable to parse revision/author from line:\n%s\n", buffer);
			state = 1;
			continue;
		}
		
		// state 1 expects the "Changed paths:" header
		if (state == 1)
		{
			if (strncmp(buffer, "Changed paths:", 14) != 0)
				printf("Expected \"Changed paths:\" on line:\n%s\n", buffer);
			state = 2;
			continue;
		}
		
		// state 2 expects filenames terminated by a blank line
		if (state == 2)
		{
			if ((buffer[0] == 'A' || buffer[0] == 'D' || buffer[0] == 'M') && buffer[1] == ' ' && buffer[2] == '/')
			{
				numfiles++;
				continue;
			}
			state = 3;
			paragraph[0] = 0;
			continue;
		}
		
		// state 3 parses lines of text
		if (state == 3)
		{
state_3:
			// look for 'new' as the starting line
			if (tolower(buffer[0]) == 'n' && 
				tolower(buffer[1]) == 'e' && 
				tolower(buffer[2]) == 'w')
			{
				if (stristr(buffer, "clone"))
				{
					flush_paragraph_newline(paragraph);
					state = 6;
					continue;
				}
				else if (stristr(buffer, "not") && stristr(buffer, "working") && !stristr(buffer, "promot"))
				{
					flush_paragraph_newline(paragraph);
					state = 7;
					continue;
				}
				else if (stristr(buffer, "game") || stristr(buffer, "working"))
				{
					flush_paragraph_newline(paragraph);
					state = 5;
					continue;
				}
			}
		
			// flush if we hit a blank line
			if (buffer[0] == 0)
			{
				flush_paragraph_newline(paragraph);
				continue;
			}
			
			// move to state 4 if we hit an asterisk or dash
			else if (buffer[0] == '*' || buffer[0] == '-')
			{
				flush_paragraph(paragraph);
				state = 4;
				// fall through
			}
			
			// otherwise, accumulate text
			else
			{
				int curlen = strlen(paragraph);
				if (curlen > 0 && paragraph[curlen - 1] != ' ')
					paragraph[curlen++] = ' ';
				strcpy(&paragraph[curlen], buffer);
				continue;
			}
		}
		
		// state 4 parses * or - list items
		if (state == 4)
		{
			// flush if we hit a blank line and go back to parsing paragraphs
			if (buffer[0] == 0)
			{
				flush_line(paragraph);
				state = 3;
				continue;
			}
			
			// flush if we hit a new line entry
			else if (buffer[0] == '*' || buffer[0] == '-')
			{
				flush_line(paragraph);
				strcpy(paragraph, buffer);
				continue;
			}
			
			// otherwise, accumulate text
			else
			{
				int curlen = strlen(paragraph);
				if (curlen > 0 && paragraph[curlen - 1] != ' ')
					paragraph[curlen++] = ' ';
				strcpy(&paragraph[curlen], buffer);
				continue;
			}
		}
		
		// states 5-7 are for new games, new clones, and new non-working
		if (state >= 5 && state <= 7)
		{
			int index = state - 5;
			char *laststring = (nextnew[index] > 0) ? newlist[index][nextnew[index] - 1] : NULL;
			char *alloc;
			
			// blank lines are ignored
			if (buffer[0] == 0)
				continue;
			
			// ignore dashed lines
			if (buffer[0] == '-' && buffer[1] == '-')
				continue;
			
			// look for 'new' as the starting line
			if (tolower(buffer[0]) == 'n' && 
				tolower(buffer[1]) == 'e' && 
				tolower(buffer[2]) == 'w')
				goto state_3;

			// if we start with a space, append a new entry
			if (spaces_removed > 0 && laststring != NULL)
			{
				nextnew[index]--;
				alloc = malloc(strlen(laststring) + strlen(buffer) + 10 + strlen(author));
				strcpy(alloc, laststring);
				if (alloc[strlen(alloc) - 1] != ' ')
					strcat(alloc, " ");
			}
			else
			{
				alloc = malloc(strlen(buffer) + 10 + strlen(author));
				alloc[0] = 0;
			}
			
			// allocate a new entry
			strcat(alloc, buffer);
			if (strchr(alloc, '[') == NULL)
				sprintf(&alloc[strlen(alloc)], " [%s]", author);
			newlist[index][nextnew[index]++] = alloc;
			continue;
		}
	}
	
	if (nextnew[0] > 0)
	{
		printf("\n\nNew machines added or promoted from NOT_WORKING status\n"
			   	   "------------------------------------------------------\n");
		print_list(0);
	}

	if (nextnew[1] > 0)
	{
		printf("\n\nNew clones added or promoted from NOT_WORKING status\n"
			  	   "----------------------------------------------------\n");
		print_list(1);
	}

	if (nextnew[2] > 0)
	{
		printf("\n\nNew machines marked as NOT_WORKING\n"
				   "----------------------------------\n");
		print_list(2);
	}

	printf("\n\nNew clones marked as NOT_WORKING\n"
			   "--------------------------------\n\n");
	printf("\n\nNew WORKING software list additions\n"
			   "-----------------------------------\n\n");
	printf("\n\nNew NOT_WORKING software list additions\n"
			   "---------------------------------------\n\n");
	return 0;
}
